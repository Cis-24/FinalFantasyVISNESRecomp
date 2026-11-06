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
add_executable(ff6_cosim_ref
    ${GR}/snesrecomp/cosim/ref_driver.c
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
