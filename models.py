import numpy as np

import backend
import nn

class Model(object):
    """Base model class for the different applications"""
    def __init__(self):
        self.get_data_and_monitor = None
        self.learning_rate = 0.0

    def run(self, x, y=None):
        raise NotImplementedError("Model.run must be overridden by subclasses")

    def train(self):
        """
        Train the model.

        `get_data_and_monitor` will yield data points one at a time. In between
        yielding data points, it will also monitor performance, draw graphics,
        and assist with automated grading. The model (self) is passed as an
        argument to `get_data_and_monitor`, which allows the monitoring code to
        evaluate the model on examples from the validation set.
        """
        for x, y in self.get_data_and_monitor(self):
            graph = self.run(x, y)
            graph.backprop()
            graph.step(self.learning_rate)

class RegressionModel(Model):
    """
    A neural network model for approximating a function that maps from real
    numbers to real numbers. The network should be sufficiently large to be able
    to approximate sin(x) on the interval [-2pi, 2pi] to reasonable precision.
    """
    def __init__(self):
        Model.__init__(self)
        self.get_data_and_monitor = backend.get_data_and_monitor_regression

        # Remember to set self.learning_rate!
        # You may use any learning rate that works well for your architecture

        self.learning_rate = 0.05

        # hidden layer size
        self.hidden_layer_size = 100

        # these four parameters are going to be trained
        self.W1 = nn.Variable(1, self.hidden_layer_size)
        self.b1 = nn.Variable(self.hidden_layer_size)
        self.W2 = nn.Variable(self.hidden_layer_size, 1)
        self.b2 = nn.Variable(1)


    def run(self, x, y=None):
        """
        Runs the model for a batch of examples.

        The correct outputs `y` are known during training, but not at test time.
        If correct outputs `y` are provided, this method must construct and
        return a nn.Graph for computing the training loss. If `y` is None, this
        method must instead return predicted y-values.

        Inputs:
            x: a (batch_size x 1) numpy array
            y: a (batch_size x 1) numpy array, or None
        Output:
            (if y is not None) A nn.Graph instance, where the last added node is
                the loss
            (if y is None) A (batch_size x 1) numpy array of predicted y-values

        Note: DO NOT call backprop() or step() inside this method!
        """

        # take it through the process up until the SquareLoss node
        # if y is provided, add the SquareLoss node, return the graph
        # if y is not provided, just return the output of the graph (without the SquareLoss node)

        #batch_size = x.shape[0]

        # set up the graph
        regressionGraph = nn.Graph([self.W1, self.b1, self.W2, self.b2])
        input_x = nn.Input(regressionGraph, x)
        xW1 = nn.MatrixMultiply(regressionGraph, input_x, self.W1)
        xW1_plus_b1 = nn.MatrixVectorAdd(regressionGraph, xW1, self.b1)
        ReLU_1 = nn.ReLU(regressionGraph, xW1_plus_b1)
        R1W2 = nn.MatrixMultiply(regressionGraph, ReLU_1, self.W2)
        R1W2_plus_b2 = nn.MatrixVectorAdd(regressionGraph, R1W2, self.b2)

        if y is not None:
            # At training time, the correct output `y` is known.
            # Here, you should construct a loss node, and return the nn.Graph
            # that the node belongs to. The loss node must be the last node
            # added to the graph.
            input_y = nn.Input(regressionGraph, y)
            R1W2_plus_b2_SL_y = nn.SquareLoss(regressionGraph, R1W2_plus_b2, input_y)
            return regressionGraph

        else:
            # At test time, the correct output is unknown.
            # You should instead return your model's prediction as a numpy array
            return regressionGraph.get_output(R1W2_plus_b2)

class OddRegressionModel(Model):
    """
    A neural network model for approximating a function that maps from real
    numbers to real numbers.

    Unlike RegressionModel, the OddRegressionModel must be structurally
    constrained to represent an odd function, i.e. it must always satisfy the
    property f(x) = -f(-x) at all points during training.
    """
    def __init__(self):
        Model.__init__(self)
        self.get_data_and_monitor = backend.get_data_and_monitor_regression

        # Remember to set self.learning_rate!
        # You may use any learning rate that works well for your architecture

        self.learning_rate = 0.0875

        # hidden layer size
        self.hidden_layer_size = 100

        # these four parameters are going to be trained
        self.W1 = nn.Variable(1, self.hidden_layer_size)
        self.b1 = nn.Variable(self.hidden_layer_size)
        self.W2 = nn.Variable(self.hidden_layer_size, 1)
        self.b2 = nn.Variable(1)

    def run(self, x, y=None):
        """
        Runs the model for a batch of examples.

        The correct outputs `y` are known during training, but not at test time.
        If correct outputs `y` are provided, this method must construct and
        return a nn.Graph for computing the training loss. If `y` is None, this
        method must instead return predicted y-values.

        Inputs:
            x: a (batch_size x 1) numpy array
            y: a (batch_size x 1) numpy array, or None
        Output:
            (if y is not None) A nn.Graph instance, where the last added node is
                the loss
            (if y is None) A (batch_size x 1) numpy array of predicted y-values

        Note: DO NOT call backprop() or step() inside this method!
        """

        #batch_size = x.shape[0]

        # set up the graph
        oddRegressionGraph = nn.Graph([self.W1, self.b1, self.W2, self.b2])
        input_x = nn.Input(oddRegressionGraph, x)
        xW1 = nn.MatrixMultiply(oddRegressionGraph, input_x, self.W1)
        xW1_plus_b1 = nn.MatrixVectorAdd(oddRegressionGraph, xW1, self.b1)
        ReLU_1 = nn.ReLU(oddRegressionGraph, xW1_plus_b1)
        R1W2 = nn.MatrixMultiply(oddRegressionGraph, ReLU_1, self.W2)
        R1W2_plus_b2 = nn.MatrixVectorAdd(oddRegressionGraph, R1W2, self.b2)

        negx = nn.Input(oddRegressionGraph, x*-1)
        negxW1 = nn.MatrixMultiply(oddRegressionGraph, negx, self.W1)
        negxW1_plus_b1 = nn.MatrixVectorAdd(oddRegressionGraph, negxW1, self.b1)
        ReLU_2 = nn.ReLU(oddRegressionGraph, negxW1_plus_b1)
        R2W2 = nn.MatrixMultiply(oddRegressionGraph, ReLU_2, self.W2)
        R2W2_plus_b2 = nn.MatrixVectorAdd(oddRegressionGraph, R2W2, self.b2)
        #neg2R2W2_plus_b2 = nn.Input(oddRegressionGraph, oddRegressionGraph.get_output(R2W2_plus_b2)*-2)
        #negR2W2_plus_b2 = nn.Add(oddRegressionGraph, R2W2_plus_b2, neg2R2W2_plus_b2)
        negR2W2_plus_b2 = nn.Input(oddRegressionGraph, oddRegressionGraph.get_output(R2W2_plus_b2)*-1)

        sumMatrix = nn.Add(oddRegressionGraph, R1W2_plus_b2, negR2W2_plus_b2)

        if y is not None:
            # At training time, the correct output `y` is known.
            # Here, you should construct a loss node, and return the nn.Graph
            # that the node belongs to. The loss node must be the last node
            # added to the graph.
            input_y = nn.Input(oddRegressionGraph, y)
            sumMatrix_SL_y = nn.SquareLoss(oddRegressionGraph, sumMatrix, input_y)
            return oddRegressionGraph
        else:
            # At test time, the correct output is unknown.
            # You should instead return your model's prediction as a numpy array
            return oddRegressionGraph.get_output(sumMatrix)

class DigitClassificationModel(Model):
    """
    A model for handwritten digit classification using the MNIST dataset.

    Each handwritten digit is a 28x28 pixel grayscale image, which is flattened
    into a 784-dimensional vector for the purposes of this model. Each entry in
    the vector is a floating point number between 0 and 1.

    The goal is to sort each digit into one of 10 classes (number 0 through 9).

    (See RegressionModel for more information about the APIs of different
    methods here. We recommend that you implement the RegressionModel before
    working on this part of the project.)
    """
    def __init__(self):
        Model.__init__(self)
        self.get_data_and_monitor = backend.get_data_and_monitor_digit_classification

        # Remember to set self.learning_rate!
        # You may use any learning rate that works well for your architecture

        self.learning_rate = 0.25

        # hidden layer size
        self.hidden_layer_size = 300

        # these four parameters are going to be trained
        self.W1 = nn.Variable(784, self.hidden_layer_size)
        self.b1 = nn.Variable(self.hidden_layer_size)
        self.W2 = nn.Variable(self.hidden_layer_size, 10)
        self.b2 = nn.Variable(10)

    def run(self, x, y=None):
        """
        Runs the model for a batch of examples.

        The correct labels are known during training, but not at test time.
        When correct labels are available, `y` is a (batch_size x 10) numpy
        array. Each row in the array is a one-hot vector encoding the correct
        class.

        Your model should predict a (batch_size x 10) numpy array of scores,
        where higher scores correspond to greater probability of the image
        belonging to a particular class. You should use `nn.SoftmaxLoss` as your
        training loss.

        Inputs:
            x: a (batch_size x 784) numpy array
            y: a (batch_size x 10) numpy array, or None
        Output:
            (if y is not None) A nn.Graph instance, where the last added node is
                the loss
            (if y is None) A (batch_size x 10) numpy array of scores (aka logits)
        """

        #batch_size = x.shape[0]
        #num_pixels = x.shape[1]

        # set up the graph
        dcGraph = nn.Graph([self.W1, self.b1, self.W2, self.b2])
        input_x = nn.Input(dcGraph, x)
        xW1 = nn.MatrixMultiply(dcGraph, input_x, self.W1)
        xW1_plus_b1 = nn.MatrixVectorAdd(dcGraph, xW1, self.b1)
        ReLU_1 = nn.ReLU(dcGraph, xW1_plus_b1)
        R1W2 = nn.MatrixMultiply(dcGraph, ReLU_1, self.W2)
        R1W2_plus_b2 = nn.MatrixVectorAdd(dcGraph, R1W2, self.b2)

        if y is not None:
            input_y = nn.Input(dcGraph, y)
            R1W2_plus_b2_SML_y = nn.SoftmaxLoss(dcGraph, R1W2_plus_b2, input_y)
            return dcGraph
        else:
            return dcGraph.get_output(R1W2_plus_b2)


class DeepQModel(Model):
    """
    A model that uses a Deep Q-value Network (DQN) to approximate Q(s,a) as part
    of reinforcement learning.

    (We recommend that you implement the RegressionModel before working on this
    part of the project.)
    """
    def __init__(self):
        Model.__init__(self)
        self.get_data_and_monitor = backend.get_data_and_monitor_rl

        self.num_actions = 2
        self.state_size = 4

        # Remember to set self.learning_rate!
        # You may use any learning rate that works well for your architecture

        self.learning_rate = 0.04166

        # hidden layer size
        self.hidden_layer_size = 50

        # these four parameters are going to be trained
        self.W1 = nn.Variable(self.state_size, self.hidden_layer_size)
        self.b1 = nn.Variable(self.hidden_layer_size)
        self.W2 = nn.Variable(self.hidden_layer_size, self.num_actions)
        self.b2 = nn.Variable(self.num_actions)


    def run(self, states, Q_target=None):
        """
        Runs the DQN for a batch of states.

        The DQN takes the state and computes Q-values for all possible actions
        that can be taken. That is, if there are two actions, the network takes
        as input the state s and computes the vector [Q(s, a_1), Q(s, a_2)]

        When Q_target == None, return the matrix of Q-values currently computed
        by the network for the input states.

        When Q_target is passed, it will contain the Q-values which the network
        should be producing for the current states. You must return a nn.Graph
        which computes the training loss between your current Q-value
        predictions and these target values, using nn.SquareLoss.

        Inputs:
            states: a (batch_size x 4) numpy array
            Q_target: a (batch_size x 2) numpy array, or None
        Output:
            (if Q_target is not None) A nn.Graph instance, where the last added
                node is the loss
            (if Q_target is None) A (batch_size x 2) numpy array of Q-value
                scores, for the two actions
        """

        # set up the graph
        dqGraph = nn.Graph([self.W1, self.b1, self.W2, self.b2])
        input_x = nn.Input(dqGraph, states)
        xW1 = nn.MatrixMultiply(dqGraph, input_x, self.W1)
        xW1_plus_b1 = nn.MatrixVectorAdd(dqGraph, xW1, self.b1)
        ReLU_1 = nn.ReLU(dqGraph, xW1_plus_b1)
        R1W2 = nn.MatrixMultiply(dqGraph, ReLU_1, self.W2)
        R1W2_plus_b2 = nn.MatrixVectorAdd(dqGraph, R1W2, self.b2)

        if Q_target is not None:
            input_y = nn.Input(dqGraph, Q_target)
            R1W2_plus_b2_SL_y = nn.SquareLoss(dqGraph, R1W2_plus_b2, input_y)
            return dqGraph

        else:
            return dqGraph.get_output(R1W2_plus_b2)

    def get_action(self, state, eps):
        """
        Select an action for a single state using epsilon-greedy.

        Inputs:
            state: a (1 x 4) numpy array
            eps: a float, epsilon to use in epsilon greedy
        Output:
            the index of the action to take (either 0 or 1, for 2 actions)
        """
        if np.random.rand() < eps:
            return np.random.choice(self.num_actions)
        else:
            scores = self.run(state)
            return int(np.argmax(scores))


class LanguageIDModel(Model):
    """
    A model for language identification at a single-word granularity.

    (See RegressionModel for more information about the APIs of different
    methods here. We recommend that you implement the RegressionModel before
    working on this part of the project.)
    """
    def __init__(self):
        Model.__init__(self)
        self.get_data_and_monitor = backend.get_data_and_monitor_lang_id

        # Our dataset contains words from five different languages, and the
        # combined alphabets of the five languages contain a total of 47 unique
        # characters.
        # You can refer to self.num_chars or len(self.languages) in your code
        self.num_chars = 47
        self.languages = ["English", "Spanish", "Finnish", "Dutch", "Polish"]

        # Remember to set self.learning_rate!
        # You may use any learning rate that works well for your architecture

        self.learning_rate = 0.06

        # hidden layer size
        self.hidden_layer_size = 300

        # these four parameters are going to be trained
        self.W1 = nn.Variable(self.num_chars, self.hidden_layer_size)
        self.b1 = nn.Variable(self.hidden_layer_size)
        self.W2 = nn.Variable(self.hidden_layer_size, len(self.languages))
        self.b2 = nn.Variable(len(self.languages))


    def run(self, xs, y=None):
        """
        Runs the model for a batch of examples.

        Although words have different lengths, our data processing guarantees
        that within a single batch, all words will be of the same length (L).

        Here `xs` will be a list of length L. Each element of `xs` will be a
        (batch_size x self.num_chars) numpy array, where every row in the array
        is a one-hot vector encoding of a character. For example, if we have a
        batch of 8 three-letter words where the last word is "cat", we will have
        xs[1][7,0] == 1. Here the index 0 reflects the fact that the letter "a"
        is the initial (0th) letter of our combined alphabet for this task.

        The correct labels are known during training, but not at test time.
        When correct labels are available, `y` is a (batch_size x 5) numpy
        array. Each row in the array is a one-hot vector encoding the correct
        class.

        Your model should use a Recurrent Neural Network to summarize the list
        `xs` into a single node that represents a (batch_size x hidden_size)
        array, for your choice of hidden_size. It should then calculate a
        (batch_size x 5) numpy array of scores, where higher scores correspond
        to greater probability of the word originating from a particular
        language. You should use `nn.SoftmaxLoss` as your training loss.

        Inputs:
            xs: a list with L elements (one per character), where each element
                is a (batch_size x self.num_chars) numpy array
            y: a (batch_size x 5) numpy array, or None
        Output:
            (if y is not None) A nn.Graph instance, where the last added node is
                the loss
            (if y is None) A (batch_size x 5) numpy array of scores (aka logits)

        Hint: you may use the batch_size variable in your code
        """
        batch_size = xs[0].shape[0]

        #for future use -- don't worry
        ReLU_1 = None

        langIDGraph = nn.Graph([self.W1, self.b1, self.W2, self.b2])

        curInput = np.zeros((batch_size, self.hidden_layer_size))
        input_h = nn.Input(langIDGraph, curInput)
        for i in range(len(xs)):

            curLetter = xs[i]

            input_c = nn.Input(langIDGraph, curLetter)
            cW1 = nn.MatrixMultiply(langIDGraph, input_c, self.W1)
            cW1_plus_b1 = nn.MatrixVectorAdd(langIDGraph, cW1, self.b1)
            cW1_plus_b1_add_h = nn.Add(langIDGraph, cW1_plus_b1, input_h)
            ReLU_1 = nn.ReLU(langIDGraph, cW1_plus_b1_add_h)

            input_h = ReLU_1


        R1W2 = nn.MatrixMultiply(langIDGraph, ReLU_1, self.W2)
        R1W2_plus_b2 = nn.MatrixVectorAdd(langIDGraph, R1W2, self.b2)



        if y is not None:
            input_y = nn.Input(langIDGraph, y)
            R1W2_plus_b2_SML_y = nn.SoftmaxLoss(langIDGraph, R1W2_plus_b2, input_y)
            return langIDGraph
        else:
            return langIDGraph.get_output(R1W2_plus_b2)
