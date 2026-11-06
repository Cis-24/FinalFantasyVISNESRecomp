/* Symbols the runner device sources reference that snesrecomp/cosim/ref_driver.c does not
 * define at the current pin. The reference has no interpreter bridge and no tier-2 capture
 * (and FF6 has no SA-1, whose sa1.c pulls in the capture hook). DEV/DIAGNOSTICS ONLY. */
#include <stdint.h>

int g_interp_apu_driving = 0;
int g_tier2_capture_active = 0;

void tier2_capture_cpu_instruction(uint8_t processor, uint32_t pc, uint8_t mx,
                                   uint8_t emulation, unsigned guest_cycles) {
    (void)processor; (void)pc; (void)mx; (void)emulation; (void)guest_cycles;
}
