import numpy as np

class KalmanFilter:
    def __init__(self):
        self.state = np.zeros(2)
        self.uncertainty = np.eye(2)
        self.measurement_noise = 0.2
        self.process_noise = 1e-8

    def reset(self, measurement):
        self.state = np.array(measurement[:2])
        self.uncertainty = np.eye(2)
        return self.state

    def predict(self):
        F = np.eye(2)  # State transition model (identity for static object)
        Q = np.eye(2) * self.process_noise  # Process noise covariance
        self.state = F @ self.state  # State prediction
        self.uncertainty = F @ self.uncertainty @ F.T + Q  # Uncertainty prediction

    def calculate_kalman_gain(self, measurement_uncertainty):
        return self.uncertainty @ np.linalg.inv(self.uncertainty + measurement_uncertainty)

    def update_state(self, measurement, kalman_gain):
        self.state = self.state + kalman_gain @ (measurement - self.state)

    def update_uncertainty(self, kalman_gain):
        self.uncertainty = (np.eye(2) - kalman_gain) @ self.uncertainty

    def update(self, dt, measurement):
        self.predict()

        # Measurement update step
        measurement = np.array(measurement[:2])
        measurement_uncertainty = np.eye(2) * self.measurement_noise**2

        # Calculate Kalman gain
        kalman_gain = self.calculate_kalman_gain(measurement_uncertainty)

        # Update state
        self.update_state(measurement, kalman_gain)

        # Update uncertainty
        self.update_uncertainty(kalman_gain)

        return self.state

class FilterRandomNoise():
    def __init__(self, process_noise=1e-9):
        self.state = np.zeros(2)  # Initial state
        self.uncertainty = np.eye(2)  # Initial uncertainty
        self.process_noise = process_noise  # Process noise covariance

    def reset(self, measurement):
        self.state = np.array(measurement[:2])
        self.uncertainty = np.eye(2)
        return self.state

    def predict(self):
        F = np.eye(2)  # State transition model (identity for static object)
        Q = np.eye(2) * self.process_noise  # Process noise covariance
        self.state = F @ self.state  # State prediction
        self.uncertainty = F @ self.uncertainty @ F.T + Q  # Uncertainty prediction

    def calculate_kalman_gain(self, measurement_uncertainty):
        return self.uncertainty @ np.linalg.inv(self.uncertainty + measurement_uncertainty)

    def update_state(self, measurement, kalman_gain):
        self.state = self.state + kalman_gain @ (measurement - self.state)

    def update_uncertainty(self, kalman_gain):
        self.uncertainty = (np.eye(2) - kalman_gain) @ self.uncertainty

    def update(self,dt, measurement):
        self.predict()

        # Measurement update step
        measurement_position = np.array(measurement[:2])
        measurement_covariance = np.array(measurement[2:]).reshape(2, 2)

        # Calculate Kalman gain
        kalman_gain = self.calculate_kalman_gain(measurement_covariance)

        # Update state
        self.update_state(measurement_position, kalman_gain)

        # Update uncertainty
        self.update_uncertainty(kalman_gain)

        return self.state
    
class AngularKalmanFilter:
    def __init__(self, process_noise=1e-5):
        self.state = np.zeros(2)  # Initial state (x, y)
        self.uncertainty = np.eye(2)  # Initial uncertainty
        self.process_noise = process_noise  # Process noise covariance
        self.measurement_noise_covariance = np.array([[0.0100, 0.0000],
                                                      [0.0000, 0.0025]])  # Measurement noise covariance

    def reset(self, measurement):
        r, phi = measurement
        self.state = np.array([r * np.cos(phi), r * np.sin(phi)])
        self.uncertainty = np.eye(2)
        return self.state

    def predict(self):
        F = np.eye(2)  # State transition model (identity for static object)
        Q = np.eye(2) * self.process_noise  # Process noise covariance
        self.state = F @ self.state  # State prediction
        self.uncertainty = F @ self.uncertainty @ F.T + Q  # Uncertainty prediction

    def calculate_kalman_gain(self, measurement_uncertainty):
        return self.uncertainty @ np.linalg.inv(self.uncertainty + measurement_uncertainty)

    def update_state(self, measurement, kalman_gain):
        self.state = self.state + kalman_gain @ measurement

    def update_uncertainty(self, kalman_gain, H):
        self.uncertainty = (np.eye(2) - kalman_gain @ H) @ self.uncertainty

    def update(self, dt, measurement):
        self.predict()

        # Measurement update step
        r_measured, phi_measured = measurement
        x, y = self.state
        r_pred = np.sqrt(x**2 + y**2)
        phi_pred = np.arctan2(y, x)
        
        # Measurement residual
        z_pred = np.array([r_pred, phi_pred])
        z_meas = np.array([r_measured, phi_measured])
        y_k = z_meas - z_pred

        # Jacobian of the measurement model
        H = np.array([
            [x / r_pred, y / r_pred],
            [-y / (r_pred**2), x / (r_pred**2)]
        ])

        # Measurement noise covariance
        R = self.measurement_noise_covariance

        # Calculate Kalman gain
        S = H @ self.uncertainty @ H.T + R
        K = self.uncertainty @ H.T @ np.linalg.inv(S)

        # Update state
        self.update_state(y_k, K)

        # Update uncertainty
        self.update_uncertainty(K, H)

        return self.state