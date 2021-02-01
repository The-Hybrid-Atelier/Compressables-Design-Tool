import copy
import matplotlib.pyplot as plt
# Keeps a record of control-loop relevant values
# Produces pretty plots for behavior analysis
class Log:
  def __init__(self, name, step_size): 
    self.name = name
    self.log = []
    self.start_t = None
    self.step_size = step_size
  def add(self, t, setpoint, process_value, action):
    if len(self.log) == 0:
      self.start_t = t
    self.log.append((t - self.start_t, setpoint, process_value, action))
  def get_t(self):
    return [t for (t, process_value, setpoint, action) in self.log]
  def get_actions(self):
    return [action for (t, process_value, setpoint, action) in self.log]
  def get_setpoints(self):
    return [setpoint for (t, process_value, setpoint, action) in self.log]
  def get_process_values(self):
    return [process_value for (t, process_value, setpoint, action) in self.log]
  def clear(self):
    self.log = []
  def policy_size(self, policies):
    # return 5
    # Convert policy data structure into np-friendly averages
    y = copy.deepcopy(policies)
    # y = y.reshape(-1)
    # y = np.array([len(lst) for lst in y])
    # number_of_policy_updates = sum(y)
    # y = y.reshape(255, 512)
    return 5
    return number_of_policy_updates

  def plot(self):
    plt.plot(self.get_t(), self.get_setpoints(), 'b--', label = "setpoints")
    plt.plot(self.get_t(), self.get_process_values(), 'r', label = "process_values")
    plt.xlabel("Time (s)")
    plt.ylabel("Pressure")
    plt.ylim(120, 135)
    plt.title('Control Log: %s (step: %2.2f s)' % (self.name, self.step_size))
    # plt.legend()
    plt.show()
  def plot_error(self):
    error = np.array(self.get_setpoints()) - np.array(self.get_process_values())
    plt.plot(self.get_t(), error, 'r')
    plt.xlabel("Time (s)")
    plt.ylabel("Error")
    plt.ylim(-50, 50)
    plt.title('Error Plot: %s (step: %2.2f s)' % (self.name, self.step_size))
    plt.show()
  def plot_action(self):
    plt.plot(self.get_t(), self.get_actions(), 'r')
    plt.xlabel("Time (s)")
    plt.ylabel("PWM")
    plt.ylim(0, 100)
    plt.title('Action Plot: %s (step: %2.2f s)' % (self.name, self.step_size))
    plt.show()