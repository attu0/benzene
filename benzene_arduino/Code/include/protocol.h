#pragma once
#include <stdint.h>

// ---------------------------------------------------------------------------
// The Uno understands TWO things on the same serial port:
//
// 1) BINARY frames (for the ROS host node). Little-endian.
//
//   frame = 0xAA 0x55 | LEN | TYPE | payload... | CRC8
//   LEN   = 1 (TYPE) + payload length
//   CRC8  = poly 0x07, init 0, computed over LEN, TYPE and payload
//
//   host -> uno
//     0x01 CMD_VEL    int16 left_tps, int16 right_tps    target ticks/s
//     0x02 RESET_ENC  (no payload)
//     0x03 SET_PID    float kp, float ki, float kd
//   uno -> host
//     0x81 STATE      uint32 stamp_us, int32 ticks_l, int32 ticks_r,
//                     int16 vel_l_tps, int16 vel_r_tps, uint8 flags
//
//   STATE frames are streamed at 50 Hz, but ONLY after the first valid binary
//   frame arrives.
//
// 2) TEXT lines (for typing in a serial monitor), see console.h.
//   Receiving a text line switches the STATE stream OFF so the monitor stays
//   readable; the next binary frame switches it back ON.
// ---------------------------------------------------------------------------
namespace protocol {

constexpr uint8_t T_CMD_VEL   = 0x01;
constexpr uint8_t T_RESET_ENC = 0x02;
constexpr uint8_t T_SET_PID   = 0x03;
constexpr uint8_t T_STATE     = 0x81;

constexpr uint8_t FLAG_WATCHDOG = 0x01;   // command watchdog has tripped

struct StateMsg {
  uint32_t stamp_us;
  int32_t  ticks_l, ticks_r;
  int16_t  vel_l, vel_r;
  uint8_t  flags;
};

// Callbacks run from poll(), never from an interrupt. Any may be null.
struct Handlers {
  void (*onCmdVel)(int16_t left_tps, int16_t right_tps);
  void (*onResetEnc)();
  void (*onSetPid)(float kp, float ki, float kd);
  void (*onTextLine)(char *line);     // one typed line, newline stripped
};

void init(const Handlers &h);
void poll();                          // drain Serial, parse frames/lines, fire callbacks
bool streaming();                     // true once a binary host has spoken (and no text since)
void sendState(const StateMsg &s);

}  // namespace protocol