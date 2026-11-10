/*
 * Final Fantasy VI: per-game runtime glue.
 *
 * THIS FILE IS THE PORT. Everything else the scaffold produced is layout,
 * build wiring, and packaging; this is where the actual work happens.
 *
 * The framework does not, and cannot, drive an arbitrary SNES game on its
 * own. Two responsibilities always land on the game host:
 *
 *   1. Deciding what "one frame" means for THIS title, and returning from
 *      run_frame() at that boundary. A real ROM's reset vector never
 *      returns (it enters a main loop that waits on vblank), so somebody
 *      has to choose the yield point.
 *   2. Delivering NMI/IRQ at the hardware edge (see
 *      snesrecomp/docs/FRAME_MODEL_HOSTS.md).
 *
 * A new port starts on the framework's beam-aligned driver
 * (runner/src/beam_frame_driver.h): one frame is one PPU field, cut at the
 * beam's vblank edge; interrupts -- raster splits and a coprocessor's IRQ
 * line -- are taken where the beam latches them; parked time still runs the
 * beam, APU and coprocessors; and the field is rasterized from the raster
 * journal with real HDMA. It is the framework's, so a fix to it reaches this
 * port on a submodule pull.
 *
 * This file used to hold its own copy of a simpler driver: frames measured
 * from wherever the CPU last stopped, NMI delivered at an arbitrary beam
 * position, the field drawn with end-of-frame register state. A game that
 * uploads in vblank between INIDISP=$80 and $0F flickered black, and one
 * that chains raster splits fell apart. Replace these calls only for what
 * the driver does not do; MetalWarriorsSNESRecomp's src/mw_rtl.c and
 * GundamWingEndlessDuelSNESRecomp's src/game_rtl.c are developed examples of
 * title-specific drivers.
 */

#include "game_rtl.h"

#include <stdio.h>

#include "beam_frame_driver.h"
#include "snes/interp_bridge.h"

/* Declared idle polls (snesrecomp/docs/IDLE_POLL.md). Performance only: the
 * bridge replays the wait with the cycles it measured, and refuses whenever a
 * guard fails. Each entry is a promise that the polled byte changes only in
 * an interrupt handler while the loop runs.
 *
 *   $7E7206  cutscene WaitVBlank (ff6 src/cutscene/cutscene_main.asm:163),
 *            `lda $17 / bne`. WRAM code, interpreted by construction. $17 is
 *            set right before the loop and cleared only by CutsceneNMI
 *            (`stz $17`, cutscene_main.asm:218); NMITIMEN=$81 arms no H/V IRQ.
 *            r01: 29.9 of 52.5 M interpreted instructions sit in this loop.
 *   $C00566  field WaitVblank (ff6 src/field/reset.asm:780), `lda $55 / beq`.
 *            $55 is cleared right before the loop and raised only by FieldNMI
 *            (`inc $55`, reset.asm:289). Replayed only from FieldIRQ on: until
 *            then NMITIMEN=$A1 arms the V-IRQ and the bridge refuses (guard 6). */
static const uint32_t kIdlePolls[] = {
    0x7E7206,
    0xC00566,
};

static void GameInitialize(void)
{
    interp_bridge_clear_idle_polls();
    for (size_t i = 0; i < sizeof kIdlePolls / sizeof *kIdlePolls; i++) {
        if (!interp_bridge_set_idle_poll(kIdlePolls[i]))
            fprintf(stderr, "[game_rtl] idle poll $%06X not declared (table full)\n",
                    (unsigned)kIdlePolls[i]);
    }
}

#ifdef SNES_COSIM
#include <stdlib.h>
#include "cpu_state.h"
#include "snes/snes.h"
#include "snes/apu.h"
/* Co-sim diagnostics only (build-cosim, tools/ff6/cosim/cosim.sh): with FF6_COSIM_APU_LOG
 * set, print the SPC cycle counter at every frame cut. Logged at the start of the next
 * frame, i.e. after the frame-boundary APU sync, which is the state the co-sim checkpoint
 * sees. The reference prints the same line (ref_driver_ff6.patch, FF6_REF_APU_LOG). */
static void CosimApuLog(void)
{
    static int on = -1;
    static unsigned long long frame;
    if (on < 0) on = getenv("FF6_COSIM_APU_LOG") != NULL;
    if (!on || !g_snes || !g_snes->apu) return;
    if (frame) {
        fprintf(stderr, "[apulog] cut=%llu master=%llu spc=%llu\n", frame,
                (unsigned long long)g_cpu.master_cycles,
                (unsigned long long)g_snes->apu->portClock);
        fflush(stderr);   /* the coordinator terminates A without a flush */
    }
    frame++;
}

/* Co-sim input: with FF6_COSIM_INPUT_LOG=<file>, write the joypad 1 mask that the next
 * frame runs with, one line "frame hexmask" whenever it differs from the previous frame's;
 * frame = frames run before it, counted from reset. The reference replays the file
 * (FF6_REF_INPUT_FILE, ref_driver_ff6.patch), so a route script on A drives both sides
 * with the same input per frame (tools/ff6/cosim/cosim.sh route). */
static void CosimInputLog(void)
{
    static int init;
    static FILE *f;
    static unsigned long long frame;
    static unsigned previous;
    if (!init) {
        const char *path = getenv("FF6_COSIM_INPUT_LOG");
        init = 1;
        if (path && path[0] && !(f = fopen(path, "w")))
            fprintf(stderr, "[inputlog] cannot write '%s'\n", path);
    }
    if (f && g_snes && g_snes->input1_currentState != previous) {
        previous = g_snes->input1_currentState;
        fprintf(f, "%llu %03x\n", frame, previous);
        fflush(f);   /* the coordinator terminates A without a flush */
    }
    frame++;
}

/* Co-sim pokes: with FF6_COSIM_POKE_LOG=<file>, write every WRAM byte that changed between
 * the end of the previous frame (the state the co-sim checkpoint sees) and the start of this
 * one, as runs "frame addr hexbytes" (frame as above, addr a WRAM offset). Between frames only
 * the host writes WRAM: the route script's poke, pokefor and forcepoke
 * (desktop/host_main.c TickScript, ApplyScriptForcePokes). The reference writes the same
 * bytes before the same frame (FF6_REF_POKE_FILE, ref_driver_ff6.patch), so a route that sets
 * up its scene by poke runs the same course on both sides. */
#include <string.h>
#include "common_rtl.h"
static FILE *s_poke_log;
static uint8 *s_poke_prev;
static unsigned long long s_poke_frame;

static void CosimPokeLogBegin(void)
{
    static int init;
    if (!init) {
        const char *path = getenv("FF6_COSIM_POKE_LOG");
        init = 1;
        if (path && path[0]) {
            s_poke_log = fopen(path, "w");
            s_poke_prev = s_poke_log ? (uint8 *)malloc(sizeof g_ram) : NULL;
            if (!s_poke_prev) {
                fprintf(stderr, "[pokelog] cannot write '%s'\n", path);
                if (s_poke_log) fclose(s_poke_log);
                s_poke_log = NULL;
            }
        }
    } else if (s_poke_log) {
        for (uint32 a = 0; a < sizeof g_ram; a++) {
            if (g_ram[a] == s_poke_prev[a]) continue;
            uint32 end = a;
            while (end < sizeof g_ram && g_ram[end] != s_poke_prev[end]) end++;
            fprintf(s_poke_log, "%llu %05X ", s_poke_frame, (unsigned)a);
            for (; a < end; a++) fprintf(s_poke_log, "%02X", g_ram[a]);
            fputc('\n', s_poke_log);
        }
        fflush(s_poke_log);   /* the coordinator terminates A without a flush */
    }
    s_poke_frame++;
}

static void CosimPokeLogEnd(void)
{
    if (s_poke_log) memcpy(s_poke_prev, g_ram, sizeof g_ram);
}

/* Co-sim port log: with FF6_COSIM_PORT_LOG=<file> and FF6_COSIM_PORT_LOG_FRAMES=lo-hi, write
 * every CPU access to $2140-$2143 in frames lo..hi (frames run before, as above) as
 * "f=frame m=master spc=portClock W|R p=port v=value". Writes are logged when the
 * runtime hands them over (before it schedules them at their guest SPC cycle), reads
 * after the SPC sync, so m is the time the runtime uses for the access. The reference
 * writes the same lines (FF6_REF_PORT_LOG, ref_driver_ff6.patch). */
static FILE *s_port_log;
static unsigned long long s_port_lo, s_port_hi, s_port_frame;

static void CosimPortLine(char kind, uint16 reg, uint8 value)
{
    if (!s_port_log || s_port_frame < s_port_lo || s_port_frame > s_port_hi) return;
    fprintf(s_port_log, "f=%llu m=%llu spc=%llu %c p=%u v=%02x\n", s_port_frame,
            (unsigned long long)g_cpu.master_cycles,
            (unsigned long long)g_snes->apu->portClock, kind, (unsigned)(reg & 3), value);
}

static int CosimPortWrite(uint16 reg, uint8 value)
{
    CosimPortLine('W', reg, value);
    return 0;   /* observe only */
}

static int CosimPortRead(uint16 reg, uint8 *value)
{
    CosimPortLine('R', reg, *value);
    return 0;
}

static void CosimPortLogFrame(void)
{
    static int init;
    if (!init) {
        const char *path = getenv("FF6_COSIM_PORT_LOG");
        const char *range = getenv("FF6_COSIM_PORT_LOG_FRAMES");
        init = 1;
        if (path && path[0] && range &&
            sscanf(range, "%llu-%llu", &s_port_lo, &s_port_hi) == 2) {
            s_port_log = fopen(path, "w");
            if (s_port_log) {
                RtlAddApuPortObserver(CosimPortWrite);
                RtlAddApuPortReadObserver(CosimPortRead);
            } else {
                fprintf(stderr, "[portlog] cannot write '%s'\n", path);
            }
        }
    } else {
        s_port_frame++;
    }
    if (s_port_log) fflush(s_port_log);   /* the coordinator terminates A without a flush */
}
#endif

void GameRunOneFrame(void)
{
#ifdef SNES_COSIM
    CosimApuLog();
    CosimInputLog();
    CosimPokeLogBegin();
    CosimPortLogFrame();
#endif
    snes_beam_frame_driver_run_frame();
#ifdef SNES_COSIM
    CosimPokeLogEnd();
#endif
}

void GameDrawPpuFrame(void)
{
    snes_beam_frame_driver_draw_ppu_frame();
}

void GameSessionReset(void)
{
    /* Rematch / soft-return: clear anything that must not survive a new
     * session. recomp-ai-rules/NETPLAY.md §3: sticky state that "has always
     * been fine" is the usual desync culprit, because single-player never
     * re-enters the boot path twice in one process. */
    snes_beam_frame_driver_reset();
}

static void GameHardwareReset(void)
{
    /* Reset hotkey and script `reset`: the driver's resume point belongs to the
     * machine that was just reset. Kept, the CPU resumes its main loop against
     * zeroed WRAM and the screen stays black. */
    snes_beam_frame_driver_reset();
}

const RtlGameInfo kGameInfo = {
    .title = "finalfantasyvi",
    .initialize = &GameInitialize,
    .run_frame = &GameRunOneFrame,
    .draw_ppu_frame = &GameDrawPpuFrame,
    .save_name_prefix = "save",
    .session_reset = &GameSessionReset,
    .hardware_reset = &GameHardwareReset,
};
