 
import cv2
import serial
import time

# Arduino connection
arduino = serial.Serial('COM13', 9600, timeout=1)
time.sleep(2)

# Webcam
cap = cv2.VideoCapture(0)

# Face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

# Servo starting positions
horizontal_angle = 90.0
vertical_angle = 90.0

# Movement settings
horizontal_range = 45
vertical_range = 35
smoothness = 0.15

# Send interval
last_send = 0
send_interval = 0.04

try:
    while True:

        ret, frame = cap.read()

        if not ret:
            break

        # Mirror webcam
        frame = cv2.flip(frame, 1)

        height, width, _ = frame.shape

        center_x = width // 2
        center_y = height // 2

        gray = cv2.cvtColor(
            frame, cv2.COLOR_BGR2GRAY
        )

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(60, 60)
        )

        # Camera center
        cv2.circle(
            frame,
            (center_x, center_y),
            5,
            (255, 0, 0),
            -1
        )

        if len(faces) > 0:

            # Select largest face
            x, y, w, h = max(
                faces,
                key=lambda f: f[2] * f[3]
            )

            face_x = x + w // 2
            face_y = y + h // 2

            # Calculate face position
            error_x = (
                face_x - center_x
            ) / (width / 2)

            error_y = (
                face_y - center_y
            ) / (height / 2)

            # Target servo angles
            target_h = 90 - error_x * horizontal_range
            target_v = 90 + error_y * vertical_range

            target_h = max(45, min(135, target_h))
            target_v = max(55, min(125, target_v))

            # Smooth servo movement
            horizontal_angle += (
                target_h - horizontal_angle
            ) * smoothness

            vertical_angle += (
                target_v - vertical_angle
            ) * smoothness

            # Send commands to Arduino
            current_time = time.time()

            if current_time - last_send >= send_interval:

                command = (
                    f"{int(horizontal_angle)} "
                    f"{int(vertical_angle)}\n"
                )

                arduino.write(command.encode())
                last_send = current_time

            # Draw face tracking
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            cv2.circle(
                frame,
                (face_x, face_y),
                5,
                (0, 0, 255),
                -1
            )

            cv2.putText(
                frame,
                f"H: {int(horizontal_angle)} V: {int(vertical_angle)}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        cv2.imshow(
            "Humanoid Eye Tracking",
            frame
        )

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    arduino.close()
