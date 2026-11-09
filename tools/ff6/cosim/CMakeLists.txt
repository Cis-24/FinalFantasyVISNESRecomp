# FF6 co-sim B side (snesrecomp docs/COSIM.md, PLAN 5.2): the framework's interp816
# reference driver (snesrecomp/cosim/ref_driver.c), unchanged, over the runner's own device
# sources. The framework target smw_cosim_ref has a stale source list at the current pin
# (sa1.c, sdd1.c and three glue symbols are missing), so the target is defined here.
# DEV/DIAGNOSTICS ONLY. Built by tools/ff6/cosim/cosim.sh (build directory under WS/work).
cmake_minimum_required(VERSION 3.16)
project(ff6_cosim_ref C)
set(CMAKE_C_STANDARD 11)
get_filename_component(GR ${CMAKE_CURRENT_SOURCE_DIR}/../../.. ABSOLUTE)
set(RUNSNES ${GR}/snesrecomp/runner/src)
# FF6 variant of the driver: ref_driver_ff6.patch is applied to a copy in the build directory
# (git apply, MSYS2 has no patch). It aligns the reference with the beam frame driver: frame
# cut at the vblank edge (V=225) before the NMI, master clocks per bus transfer by region
# (snes_cycles.h, MEMSEL from $420D), internal cycles at 6, DRAM refresh 40 per 1364, and the
# $420B DMA time through snes_set_master_clock_charge_hook, the RDNMI poll window of snesrecomp
# patch 0003 (a poll parked at the frame start reads the flag before the NMI), APU port
# accesses at the start of their bus transfer (as snes9x), and the H/V timer IRQ on line VTIME
# (the driver fired it one line late).
# FF6_REF_INPUT_FILE replays the A side's joypad 1 log per frame (cosim.sh route).
set(PATCHED ${CMAKE_BINARY_DIR}/patched)
add_custom_command(
    OUTPUT ${PATCHED}/ref_driver.c
    COMMAND ${CMAKE_COMMAND} -E make_directory ${PATCHED}
    COMMAND ${CMAKE_COMMAND} -E copy ${GR}/snesrecomp/cosim/ref_driver.c ${PATCHED}/ref_driver.c
    COMMAND git apply --unsafe-paths --directory=patched ${CMAKE_CURRENT_SOURCE_DIR}/ref_driver_ff6.patch
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    DEPENDS ${GR}/snesrecomp/cosim/ref_driver.c ${CMAKE_CURRENT_SOURCE_DIR}/ref_driver_ff6.patch
    COMMENT "Applying ref_driver_ff6.patch")
add_executable(ff6_cosim_ref
    ${PATCHED}/ref_driver.c
    ref_glue.c
    ${RUNSNES}/cosim.c
    ${RUNSNES}/cosim_state.c
    ${RUNSNES}/audio_trace.c
    ${RUNSNES}/crc32.c
    ${RUNSNES}/sha256.c
    ${RUNSNES}/util.c
    ${RUNSNES}/snes/apu.c
    ${RUNSNES}/snes/cart.c
    ${RUNSNES}/snes/cx4.c
    ${RUNSNES}/snes/cpu.c
    ${RUNSNES}/snes/dma.c
    ${RUNSNES}/snes/dsp.c
    ${RUNSNES}/snes/dsp1.c
    ${RUNSNES}/snes/dsp1_hle.c
    ${RUNSNES}/snes/joypad.c
    ${RUNSNES}/snes/ppu.c
    ${RUNSNES}/snes/ppu_legacy.c
    ${RUNSNES}/snes/sa1.c
    ${RUNSNES}/snes/sdd1.c
    ${RUNSNES}/snes/snes.c
    ${RUNSNES}/snes/snes_other.c
    ${RUNSNES}/snes/spc.c
    ${RUNSNES}/snes/superfx.c
    ${RUNSNES}/snes/ws_shadow.c
    ${RUNSNES}/snes/interp816.c
    ${RUNSNES}/snes/color_lut.c
)
# ${GR}/src provides variables.h, which snes.c includes.
target_include_directories(ff6_cosim_ref PRIVATE ${RUNSNES} ${RUNSNES}/snes ${GR} ${GR}/src)
target_compile_definitions(ff6_cosim_ref PRIVATE
    SNES_COSIM SNES_COSIM_REF SNESRECOMP_TRACE=0 SDL_MAIN_HANDLED)
target_compile_options(ff6_cosim_ref PRIVATE -w -Wno-implicit-function-declaration)
target_link_libraries(ff6_cosim_ref PRIVATE m ws2_32)
