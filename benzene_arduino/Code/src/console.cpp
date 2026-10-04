#include "console.h"
#include <Arduino.h>
#include <stdlib.h>
#include "encoders.h"

namespace console {
namespace {

Actions g_a = {nullptr, nullptr, nullptr, nullptr, nullptr};

bool toInt(const char *s, long &v) {
  char *e;
  v = strtol(s, &e, 10);
  return e != s && *e == '\0';
}

bool toFloat(const char *s, float &v) {
  char *e;
  v = (float)strtod(s, &e);
  return e != s && *e == '\0';
}

int16_t clamp16(long v, long lim) {
  if (v > lim) v = lim;
  if (v < -lim) v = -lim;
  return (int16_t)v;
}

// Splits `line` in place into at most `max` space-separated tokens.
int tokenize(char *line, char *tok[], int max) {
  int n = 0;
  char *p = line;
  while (*p && n < max) {
    while (*p == ' ' || *p == '\t') *p++ = '\0';
    if (!*p) break;
    tok[n++] = p;
    while (*p && *p != ' ' && *p != '\t') p++;
  }
  return n;
}

void ok()  { Serial.println(F("OK")); }
void err() { Serial.println(F("ERR")); }

void help() {
  Serial.println(F("e            encoder ticks: left right"));
  Serial.println(F("v            speed ticks/s: left right"));
  Serial.println(F("r            reset encoders"));
  Serial.println(F("d <w> <c>    raw pin: w 0=L 1=R, c 0=A 1=B"));
  Serial.println(F("m <l> <r>    speed target ticks/s (closed loop)"));
  Serial.println(F("o <l> <r>    raw PWM -255..255 (open loop)"));
  Serial.println(F("u kp ki kd [kff]   PID gains"));
}

}  // namespace

void init(const Actions &a) { g_a = a; }

void handleLine(char *line) {
  char *t[5];
  int n = tokenize(line, t, 5);
  if (n == 0) return;
  if (t[0][1] != '\0') { err(); return; }      // commands are a single character

  long a, b;
  float f[4];
  switch (t[0][0]) {
    case 'e': {
      int32_t l, r;
      encoders::snapshot(l, r);
      Serial.print(l);
      Serial.print(' ');
      Serial.println(r);
      break;
    }
    case 'v': {
      int16_t l = 0, r = 0;
      if (g_a.getVelocity) g_a.getVelocity(l, r);
      Serial.print(l);
      Serial.print(' ');
      Serial.println(r);
      break;
    }
    case 'r':
      if (g_a.resetEncoders) { g_a.resetEncoders(); ok(); } else err();
      break;
    case 'd':
      if (n == 3 && toInt(t[1], a) && toInt(t[2], b) && (a == 0 || a == 1) && (b == 0 || b == 1))
        Serial.println((int)encoders::readChannel((uint8_t)a, (uint8_t)b));
      else err();
      break;
    case 'm':
      if (n == 3 && toInt(t[1], a) && toInt(t[2], b) && g_a.setSpeed) {
        g_a.setSpeed(clamp16(a, 32767), clamp16(b, 32767));
        ok();
      } else err();
      break;
    case 'o':
      if (n == 3 && toInt(t[1], a) && toInt(t[2], b) && g_a.setPwm) {
        g_a.setPwm(clamp16(a, 255), clamp16(b, 255));
        ok();
      } else err();
      break;
    case 'u':
      if ((n == 4 || n == 5) && g_a.setGains && toFloat(t[1], f[0]) && toFloat(t[2], f[1]) &&
          toFloat(t[3], f[2]) && (n == 4 || toFloat(t[4], f[3])) &&
          f[0] >= 0 && f[1] >= 0 && f[2] >= 0 && (n == 4 || f[3] >= 0)) {
        g_a.setGains(f[0], f[1], f[2], n == 5 ? f[3] : -1.0f);
        ok();
      } else err();
      break;
    case '?':
    case 'h':
      help();
      break;
    default:
      err();
  }
}

}  // namespace console