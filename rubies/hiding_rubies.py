import numpy as np

# https://www.youtube.com/watch?v=2QJ2L2ip32w
# Stolen Rubies Riddle
# 1.  There are 30 rubies
# 2.  Each box must have 2 rubies, one box has 6 more rubies than one of the others
# 3.  Write down a number between 1 and 30 for each box, guessing number of rubies
# 4.  You get the number of rubies you guessed, but only if your number is smaller than the actual number
# 5.  You are playing against someone else who places the rubies and gets to keep the ones you don't get

# A strategy of guessing all 8s guarantees that you'll get at least 16 rubies


placements = []

for i in range(2, 21, 2):
    if i != 10 and i != 8:
        placements.append((i, 12 - i//2, 18 - i//2))

# Find all possible guesses
# All configurations have at least 2 rubies
# Don't guess more than 20 for any boxes since the constraints don't allow boxes to have more than 20
guesses = []

max_in_box = 20
for i in range(2, max_in_box+1):
    for j in range(i, max_in_box+1):
        for k in range(j, max_in_box+1):
            guesses.append((i, j, k))

print('{} possible guesses'.format(len(guesses)))
print('{} possible placements'.format(len(placements)))


def compute_outcome(guess, placement):
    permutations = [
        (0, 1, 2),
        (0, 2, 1),
        (1, 0, 2),
        (1, 2, 0),
        (2, 0, 1),
        (2, 1, 0)
    ]

    score = 0
    for permutation in permutations:
        for i in range(3):
            if guess[i] <= placement[permutation[i]]:
                score += guess[i]

    return score / 6


outcomes = np.zeros((len(guesses), len(placements)))


for guess_num, guess in enumerate(guesses):
    for placement_num, placement in enumerate(placements):
        outcomes[guess_num, placement_num] = compute_outcome(guess, placement)


def compute_softmax(weights):
    exp = np.exp(weights)
    exp_sum = np.sum(exp)
    out = exp / exp_sum
    return out


def update(weights, rewards, out, lr):
    grad = out * (rewards - np.dot(rewards, out))
    new_weights = weights + grad * lr
    return new_weights


def train():
    guess_weights = np.zeros(len(guesses), np.float32)  # random policies
    placement_weights = np.zeros(len(placements), np.float32)

    guess_policy = compute_softmax(guess_weights)
    placement_policy = compute_softmax(placement_weights)

    update_guesses = True
    update_placements = True

    guess_learning_rate = 0.01
    placement_learning_rate = 0.0001

    eights = guesses.index((8, 8, 8))

    for i in range(10000000):
        if i + 1 in [0, 1, 10, 25, 100, 1000, 10000] or (i + 1) % 100000 == 0:
            print("Iteration", i + 1)
            args = np.argsort(guess_policy)[::-1]
            best_guess, next_best_guess = args[:2]
            eight_rank = np.where(args == eights)[0][0]+1
            print("Best guess: {} P={}".format(guesses[best_guess], guess_policy[best_guess]))
            print("Next guess: {} P={}".format(guesses[next_best_guess], guess_policy[next_best_guess]))
            print("Eights: {} P={}, rank={}".format(guesses[eights], guess_policy[eights], eight_rank))

            for placement in range(len(placements)):
                print(placements[placement], placement_policy[placement], np.dot(outcomes[:, placement], guess_policy))
            print("Expected game value: {}".format(np.dot(np.matmul(outcomes, placement_policy), guess_policy)))
            print()

        # train guesser
        if update_guesses:
            guess_rewards = np.matmul(outcomes, placement_policy)
        if update_placements:
            placement_rewards = np.matmul(outcomes.T, guess_policy)

        if update_guesses:
            guess_weights = update(guess_weights, guess_rewards, guess_policy, guess_learning_rate)
            guess_policy = compute_softmax(guess_weights)
            # Positive rewards for guesser because he's the one getting the extra rubies

        if update_placements:
            # Negative rewards for placer because he's the one losing the extra rubies
            placement_weights = update(placement_weights, -placement_rewards, placement_policy, placement_learning_rate)
            placement_policy = compute_softmax(placement_weights)


def update_stochastic(actions, rewards, weights, out, lr):
    grad = np.zeros_like(weights)
    for action, reward in zip(actions, rewards):
        grad -= out * reward
        grad[action] += reward
    new_weights = weights + grad * lr / len(actions)
    return new_weights


def train_stochastic():
    guess_weights = np.zeros(len(guesses), np.float32)  # random policies
    placement_weights = np.zeros(len(placements), np.float32)

    guess_policy = compute_softmax(guess_weights)
    placement_policy = compute_softmax(placement_weights)

    update_guesses = True
    update_placements = True

    guess_learning_rate = 0.001
    placement_learning_rate = 0.001

    num_samples = 1000

    eights = guesses.index((8, 8, 8))

    for i in range(10000000):
        if i + 1 in [0, 1, 10, 25] or (i + 1) % 50 == 0:
            print("Iteration", i + 1)
            args = np.argsort(guess_policy)[::-1]
            best_guess, next_best_guess = args[:2]
            eight_rank = np.where(args == eights)[0][0]+1
            print("Best guess: {} P={}".format(guesses[best_guess], guess_policy[best_guess]))
            print("Next guess: {} P={}".format(guesses[next_best_guess], guess_policy[next_best_guess]))
            print("Eights: {} P={}, rank={}".format(guesses[eights], guess_policy[eights], eight_rank))

            for placement in range(len(placements)):
                print(placements[placement], placement_policy[placement], np.dot(outcomes[:, placement], guess_policy))
            print("Expected game value: {}".format(np.dot(np.matmul(outcomes, placement_policy), guess_policy)))
            print()

        # train guesser
        if update_guesses or update_placements:
            guess_actions = np.zeros(num_samples, np.int32)
            placement_actions = np.zeros(num_samples, np.int32)
            rewards = np.zeros(num_samples, np.float32)
            for i in range(num_samples):
                guess_actions[i] = np.random.choice(len(guesses), p=guess_policy)
                placement_actions[i] = np.random.choice(len(placements), p=placement_policy)
                rewards[i] = outcomes[guess_actions[i], placement_actions[i]]

        if update_guesses:
            guess_weights = update_stochastic(guess_actions, rewards, guess_weights, guess_policy, guess_learning_rate)
            guess_policy = compute_softmax(guess_weights)
            # Positive rewards for guesser because he's the one getting the extra rubies

        if update_placements:
            # Negative rewards for placer because he's the one losing the extra rubies
            placement_weights = update_stochastic(placement_actions, -rewards, placement_weights, placement_policy, placement_learning_rate)
            placement_policy = compute_softmax(placement_weights)


def main():
    train_stochastic()
    

if __name__ == '__main__':
    main()
