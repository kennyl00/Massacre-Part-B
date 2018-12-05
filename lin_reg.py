# written by Kenny Lee and Jiawei Xu
# Subject COMP30024 Artificial Intelligence
from random import *
import random
import numpy as np
#import matplotlib.pyplot as plt


filename = "data.txt"


# This function returns the Win Loss ratio
def wlrat(win, loss):
    total_games = win + loss

    try:
        rat = float(win)/float(total_games)

    except ZeroDivisionError:
        rat = 1.0

    return rat


# This function generates a new entries
def new_entry(max_step, game_won):
    if game_won:
        list = str(max_step) + ",1,0\n"
    else:
        list = str(max_step) + ",0,1\n"

    return list

# This function updates the existing data set
def update_file(max_step, game_won, color):
    step_found = False  # Flag if a step was found
    print("max_step used:", max_step)
    # read the file and close it
    with open(color+filename, "r+") as file:
        data = file.readlines()
        file.close()


    # If there is data in file
    if data:
        # Look at all the data
        for (i,line) in enumerate(data):
            tuple = line.split(',')
            step = float(tuple[0])
            win = int(tuple[1])
            los = int(tuple[2])

            # Find the matching step and update
            if step == max_step:
                new_line = None
                step_found = True
                if game_won:
                    new_line = str(step) + "," + str(win + 1) + "," + str(los) + "\n"

                else:
                    new_line = str(step) + "," + str(win) + "," + str(los + 1) + "\n"

                data[i] = new_line

        # If there is data but step was not found
        if not step_found:
            data.append(new_entry(max_step, game_won))


    # If there's no data in file
    else:
        data.append(new_entry(max_step, game_won))

    # write to the file and close it
    with open(color+filename, "w") as file:
        file.writelines(data)
        file.close()

def get_total(color):

    with open(color+filename, "r+") as file:
        data = file.readlines()
        file.close()
    total_tests = 0
    if data:
        for (i,line) in enumerate(data):
            tuple = line.split(',')
            step = float(tuple[0])
            win = int(tuple[1])
            los = int(tuple[2])

            total_tests += win
            total_tests += los
    print("total_tests:", total_tests)



# This function returns the steps
def get_step(color):
    graph = {}

    # Read the file and close it
    with open(color + filename, "r") as file:
        data = file.readlines()
        file.close()

    # Run Linear Regression predicting 100% winrates
    max_step = linear_reg(data)

    return max_step

def estimate_coef(x, y):
    # Number of observations/points
    n = np.size(x)

    # Mean of x and y vector
    m_x, m_y = np.mean(x), np.mean(y)

    # calculating cross-deviation and deviation about x
    SS_xy = np.sum(y*x - n*m_y*m_x)
    SS_xx = np.sum(x*x - n*m_x*m_x)

    # Calculate Regression Coef
    b_1 = SS_xy / SS_xx # slope
    b_0 = m_y - b_1*m_x # y intercept

    return(b_0, b_1)

def plot_regression_line(x, y, b):
    # plotting the actual points as scatter plot
    plt.scatter(x, y, color = "m",
               marker = "o", s = 30)

    # predicted response vector
    y_pred = b[0] + b[1]*x

    # plotting the regression line
    plt.plot(x, y_pred, color = "g")

    # putting labels
    plt.xlabel('x')
    plt.ylabel('y')

    # function to show plot
    plt.show()


def linear_reg(data):
    x = []  # steps
    y = []  # win ratio

    for line in data:
        tuple = line.split(',')
        step = float(tuple[0])
        wins = int(tuple[1])
        loss = int(tuple[2])

        y.append(wlrat(wins, loss))
        x.append(step)

    # Estimate coef
    b = estimate_coef(np.asarray(x), np.asarray(y))

    print("Estimated coefficients:\ny-intercept = {}  \
          \nslope = {}".format(b[0], b[1]))


    #print("STEP={}".format(round(float(1-b[0])/(b[1]),1)))
    # plotting regression line
    # plot_regression_line(np.asarray(x), np.asarray(y), b)

    return round(float(1-b[0])/(b[1]),1)


def get_random():
    return round(random.uniform(1, 2), 2)

"""
get_total("O")
get_total("@")
get_step("O")
get_step("@")
"""
