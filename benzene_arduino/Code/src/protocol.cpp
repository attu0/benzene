#include "protocol.h"
#include <Arduino.h>
#include <string.h>
#include "config.h"

namespace protocol {
namespace {

Handlers g_h = {nullptr, nullptr, nullptr, nullptr};
bool g_streaming = false;

// ----- binary frame parser state -----
constexpr uint8_t MAX_BODY = 20;           // TYPE + payload
uint8_t g_state = 0, g_len = 0, g_idx = 0, g_buf[MAX_BODY + 1];  // +1 for CRC

// ----- text line buffer -----
constexpr uint8_t LINE_MAX = 40;
char g_line[LINE_MAX + 1];
uint8_t g_lineLen = 0;
bool g_lineOverflow = false;

uint8_t crc8(uint8_t crc, uint8_t b) {
  crc ^= b;
  for (uint8_t i = 0; i < 8; i++) crc = (crc & 0x80) ? (uint8_t)((crc << 1) ^ 0x07) : (uint8_t)(crc << 1);
  return crc;
}

void dispatch(uint8_t type, const uint8_t *p, uint8_t n) {
  if (type == T_CMD_VEL && n == 4 && g_h.onCmdVel) {
    int16_t l, r;
    memcpy(&l, p, 2);
    memcpy(&r, p + 2, 2);
    g_h.onCmdVel(l, r);
  } else if (type == T_RESET_ENC && n == 0 && g_h.onResetEnc) {
    g_h.onResetEnc();
  } else if (type == T_SET_PID && n == 12 && g_h.onSetPid) {
    float kp, ki, kd;
    memcpy(&kp, p, 4);
    memcpy(&ki, p + 4, 4);
    memcpy(&kd, p + 8, 4);
    g_h.onSetPid(kp, ki, kd);
  }
}

void endOfLine() {
  if (!g_lineOverflow && g_lineLen > 0) {
    g_line[g_lineLen] = '\0';
    g_streaming = false;                    // typed text: stop the binary stream
    if (g_h.onTextLine) g_h.onTextLine(g_line);
  }
  g_lineLen = 0;
  g_lineOverflow = false;
}

void feed(uint8_t b) {
  switch (g_state) {
    case 0:
      if (b == 0xAA) {                      // start of a binary frame
        g_state = 1;
        g_lineLen = 0;
        g_lineOverflow = false;
      } else if (b == '\n' || b == '\r') {
        endOfLine();
      } else if (b >= 32 && b < 127) {      // printable: part of a typed line
        if (g_lineLen < LINE_MAX) g_line[g_lineLen++] = (char)b;
        else g_lineOverflow = true;
      }
      break;
    case 1: g_state = (b == 0x55) ? 2 : (b == 0xAA ? 1 : 0); break;
    case 2:
      if (b == 0 || b > MAX_BODY) { g_state = 0; break; }
      g_len = b; g_idx = 0; g_state = 3;
      break;
    case 3:
      g_buf[g_idx++] = b;
      if (g_idx == g_len + 1) {              // body + CRC received
        uint8_t c = crc8(0, g_len);
        for (uint8_t i = 0; i < g_len; i++) c = crc8(c, g_buf[i]);
        if (c == g_buf[g_len]) {
          g_streaming = true;                // a binary host is talking to us
          dispatch(g_buf[0], g_buf + 1, g_len - 1);
        }
        g_state = 0;
      }
      break;
  }
}

}  // namespace

void init(const Handlers &h) {
  g_h = h;
  Serial.begin(cfg::BAUD);
}

void poll() {
  while (Serial.available()) feed((uint8_t)Serial.read());
}

bool streaming() { return g_streaming; }

void sendState(const StateMsg &s) {
  uint8_t f[22];
  uint8_t *q = f;
  *q++ = 0xAA; *q++ = 0x55;
  *q++ = 18;                    // LEN = TYPE + 17 payload bytes
  *q++ = T_STATE;
  memcpy(q, &s.stamp_us, 4); q += 4;
  memcpy(q, &s.ticks_l, 4);  q += 4;
  memcpy(q, &s.ticks_r, 4);  q += 4;
  memcpy(q, &s.vel_l, 2);    q += 2;
  memcpy(q, &s.vel_r, 2);    q += 2;
  *q++ = s.flags;
  uint8_t c = 0;
  for (uint8_t i = 2; i < 21; i++) c = crc8(c, f[i]);   // LEN .. flags
  *q++ = c;
  Serial.write(f, sizeof(f));
}

}  // namespace protocol