/***************************************************************
   Motor driver function definitions - by James Nugen
   *************************************************************/

#ifdef L298_MOTOR_DRIVER
  // #define RIGHT_MOTOR_BACKWARD 5
  // #define LEFT_MOTOR_BACKWARD  6
  // #define RIGHT_MOTOR_FORWARD  9
  // #define LEFT_MOTOR_FORWARD   10
  // #define RIGHT_MOTOR_ENABLE 12
  // #define LEFT_MOTOR_ENABLE 13
  #define RIGHT_MOTOR_ENABLE 5
  #define LEFT_MOTOR_ENABLE 6
  #define RIGHT_MOTOR_FORWARD 9
  #define RIGHT_MOTOR_BACKWARD 8
  #define LEFT_MOTOR_FORWARD 10
  #define LEFT_MOTOR_BACKWARD 11
#endif

void initMotorController();
void setMotorSpeed(int i, int spd);
void setMotorSpeeds(int leftSpeed, int rightSpeed);
