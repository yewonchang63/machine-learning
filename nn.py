import numpy as np

def main():
    """
    This is sample code for linear regression, which demonstrates how to use the
    Graph class.

    Once you have answered Questions 2 and 3, you can run `python nn.py` to
    execute this code.
    """

    # This is our data, where x is a 4x2 matrix and y is a 4x1 matrix
    x = np.array([[0., 0.],
                  [0., 1.],
                  [1., 0.],
                  [1., 1.]])
    y = np.dot(x, np.array([[7.],
                            [8.]])) + 3

    # Let's construct a simple model to approximate a function from 2D
    # points to numbers, f(x) = x_0 * m_0 + x_1 * m_1 + b
    # Here m and b are variables (trainable parameters):
    m = Variable(2,1)
    b = Variable(1)

    # We train our network using batch gradient descent on our data
    for iteration in range(10000):
        # At each iteration, we first calculate a loss that measures how
        # good our network is. The graph keeps track of all operations used
        graph = Graph([m, b])
        input_x = Input(graph, x)
        input_y = Input(graph, y)
        xm = MatrixMultiply(graph, input_x, m)
        xm_plus_b = MatrixVectorAdd(graph, xm, b)
        loss = SquareLoss(graph, xm_plus_b, input_y)
        # Then we use the graph to perform backprop and update our variables
        graph.backprop()
        graph.step(0.01)

    # After training, we should have recovered m=[[7],[8]] and b=[3]
    print("Final values are: {}".format([m.data[0,0], m.data[1,0], b.data[0]]))
    assert np.isclose(m.data[0,0], 7)
    assert np.isclose(m.data[1,0], 8)
    assert np.isclose(b.data[0], 3)
    print("Success!")

class Graph(object):
    """
    A graph that keeps track of the computations performed by a neural network
    in order to implement back-propagation.

    Each evaluation of the neural network (during both training and test-time)
    will create a new Graph. The computation will add nodes to the graph, where
    each node is either a DataNode or a FunctionNode.

    A DataNode represents a trainable parameter or an input to the computation.
    A FunctionNode represents doing a computation based on two previous nodes in
    the graph.

    The Graph is responsible for keeping track of all nodes and the order they
    are added to the graph, for computing gradients using back-propagation, and
    for performing updates to the trainable parameters.

    For an example of how the Graph can be used, see the function `main` above.
    """

    def __init__(self, variables):
        """
        Initializes a new computation graph.

        variables: a list of Variable objects that store the trainable parameters
            for the neural network.

        Hint: each Variable is also a node that needs to be added to the graph,
        so don't forget to call `self.add` on each of the variables.
        """
        self.backprop_called = False
        self.nodeDict = {}      # node -> [node's forward value, node's backwards-accumulated value]
        self.nodes = []
        self.vars = []
        for var in variables:
            self.add(var)
            self.vars.append(var)

    def get_nodes(self):
        """
        Returns a list of all nodes that have been added to this Graph, in the
        order they were added. This list should include all of the Variable
        nodes that were passed to `Graph.__init__`.

        Returns: a list of nodes
        """
        return self.nodes

    def get_inputs(self, node):
        """
        Retrieves the inputs to a node in the graph. Assume the `node` has
        already been added to the graph.

        Returns: a list of numpy arrays

        Hint: every node has a `.get_parents()` method
        """
        parents = node.get_parents()
        the_inputs = []

        for parent in parents:
            the_inputs.append( self.get_output(parent) )
        return the_inputs

    def get_output(self, node):
        """
        Retrieves the output to a node in the graph. Assume the `node` has
        already been added to the graph.

        Returns: a numpy array or a scalar
        """
        if node in self.nodeDict:
            return self.nodeDict[node][0]
        else:
            return None

    def get_gradient(self, node):
        """
        Retrieves the gradient for a node in the graph. Assume the `node` has
        already been added to the graph.

        If `Graph.backprop` has already been called, this should return the
        gradient of the loss with respect to the output of the node. If
        `Graph.backprop` has not been called, it should instead return a numpy
        array with correct shape to hold the gradient, but with all entries set
        to zero.

        Returns: a numpy array
        """
        if self.backprop_called:
            if node in self.nodeDict:
                return self.nodeDict[node][1]
            else:
                return None
        else:
            return np.zeros_like(self.get_output(node))

    def add(self, node):
        """
        Adds a node to the graph.

        This method should calculate and remember the output of the node in the
        forwards pass (which can later be retrieved by calling `get_output`)
        We compute the output here because we only want to compute it once,
        whereas we may wish to call `get_output` multiple times.

        Additionally, this method should initialize an all-zero gradient
        accumulator for the node, with correct shape.
        """

        # add node to graph's list of nodes
        self.nodes.append(node)

        # get forward value
        inputs = self.get_inputs(node)
        forwardVal = node.forward(inputs)
        self.nodeDict[node] = [forwardVal]

        # now initialize all-zero gradient accumulator
        gradAccum = np.zeros_like(forwardVal)
        self.nodeDict[node].append(gradAccum)


    def backprop(self):
        """
        Runs back-propagation. Assume that the very last node added to the graph
        represents the loss.

        After back-propagation completes, `get_gradient(node)` should return the
        gradient of the loss with respect to the `node`.

        Hint: the gradient of the loss with respect to itself is 1.0, and
        back-propagation should process nodes in the exact opposite of the order
        in which they were added to the graph.
        """
        loss_node = self.get_nodes()[-1]
        assert np.asarray(self.get_output(loss_node)).ndim == 0

        self.backprop_called = True

        node_list = self.get_nodes()[::-1] # list of nodes in reverse order
        self.nodeDict[node_list[0]][1] += np.ones_like(self.nodeDict[node_list[0]][1])  # the gradient of the loss with respect to itself is 1.0

        for node in node_list:
            inputs = self.get_inputs(node)
            backwardVal = node.backward(inputs, self.get_gradient(node))

            # get parents
            parents = node.get_parents()

            assert len(parents) == len(backwardVal)
            for i in range(len(parents)):
                self.nodeDict[parents[i]][1] += backwardVal[i]



    def step(self, step_size):
        """
        Updates the values of all variables based on computed gradients.
        Assume that `backprop()` has already been called, and that gradients
        have already been computed.

        Hint: each Variable has a `.data` attribute
        """

        for var in self.vars:
            var.data -= (step_size * self.nodeDict[var][1])



class DataNode(object):
    """
    DataNode is the parent class for Variable and Input nodes.

    Each DataNode must define a `.data` attribute, which represents the data
    stored at the node.
    """

    @staticmethod
    def get_parents():
        # A DataNode has no parent nodes, only a `.data` attribute
        return []

    def forward(self, inputs):
        # The forwards pass for a data node simply returns its data
        return self.data

    @staticmethod
    def backward(inputs, gradient):
        # A DataNode has no parents or inputs, so there are no gradients to
        # compute in the backwards pass
        return []

class Variable(DataNode):
    """
    A Variable stores parameters used in a neural network.

    Variables should be created once and then passed to all future Graph
    constructors. Use `.data` to access or modify the numpy array of parameters.
    """

    def __init__(self, *shape):
        """
        Initializes a Variable with a given shape.

        For example, Variable(5) will create 5-dimensional vector variable,
        while Variable(10, 10) will create a 10x10 matrix variable.

        The initial value of the variable before training starts can have a big
        effect on how long the network takes to train. The provided initializer
        works well across a wide range of applications.
        """
        assert shape
        limit = np.sqrt(3.0 / np.mean(shape))
        self.data = np.random.uniform(low=-limit, high=limit, size=shape)

class Input(DataNode):
    """
    An Input node packages a numpy array into a node in a computation graph.
    Use this node for inputs to your neural network.

    For trainable parameters, use Variable instead.
    """

    def __init__(self, graph, data):
        """
        Initializes a new Input and adds it to a graph.
        """
        assert isinstance(data, np.ndarray), "data must be a numpy array"
        assert data.dtype.kind == "f", "data must have floating-point entries"
        self.data = data
        graph.add(self)

class FunctionNode(object):
    """
    A FunctionNode represents a value that is computed based on other nodes in
    the graph. Each function must implement both a forward and backward pass.
    """

    def __init__(self, graph, *parents):
        self.parents = parents
        graph.add(self)

    def get_parents(self):
        return self.parents

    @staticmethod
    def forward(inputs):
        raise NotImplementedError

    @staticmethod
    def backward(inputs, gradient):
        raise NotImplementedError

class Add(FunctionNode):
    """
    Adds two vectors or matrices, element-wise

    Inputs: [x, y]
        x may represent either a vector or a matrix
        y must have the same shape as x
    Output: x + y
    """

    @staticmethod
    def forward(inputs):
        assert len(inputs) == 2

        return np.add(inputs[0], inputs[1])

    @staticmethod
    def backward(inputs, gradient):
        assert len(inputs) == 2

        gradients = [gradient, gradient]

        return gradients

class MatrixMultiply(FunctionNode):
    """
    Represents matrix multiplication.

    Inputs: [A, B]
        A represents a matrix of shape (n x m)
        B represents a matrix of shape (m x k)
    Output: a matrix of shape (n x k)
    """

    @staticmethod
    def forward(inputs):
        assert len(inputs) == 2

        return np.dot(inputs[0], inputs[1])


    @staticmethod
    def backward(inputs, gradient):
        assert len(inputs) == 2

        return [np.dot(gradient, inputs[1].T), np.dot(inputs[0].T, gradient)]

class MatrixVectorAdd(FunctionNode):
    """
    Adds a vector to each row of a matrix.

    Inputs: [A, x]
        A represents a matrix of shape (n x m)
        x represents a vector (m)
    Output: a matrix of shape (n x m)
    """

    @staticmethod
    def forward(inputs):
        assert len(inputs) == 2

        return np.add(inputs[0], inputs[1].T)

    @staticmethod
    def backward(inputs, gradient):
        assert len(inputs) == 2

        return [gradient, np.sum(gradient, axis=0)]

class ReLU(FunctionNode):
    """
    An element-wise Rectified Linear Unit nonlinearity: max(x, 0).
    This nonlinearity replaces all negative entries in its input with zeros.

    Input: [x]
        x represents either a vector or matrix
    Output: same shape as x, with no negative entries
    """

    @staticmethod
    def forward(inputs):
        assert len(inputs) == 1

        zeroMatrix = np.zeros_like(inputs[0])
        return np.maximum(inputs[0], zeroMatrix)


    @staticmethod
    def backward(inputs, gradient):
        assert len(inputs) == 1

        # if input is positive, take corresponding gradient
        # else take 0

        # want to create matrix of 0's and 1's
            # contains 0 if input is negative
            # contains 1 if input is positive
        # then (element-wise) multiply this matrix with gradient

        def calcBackward(number):
            if number < 0:
                return 0
            else:
                return 1

        calcBackward = np.vectorize(calcBackward)

        return [np.multiply(calcBackward(inputs[0]), gradient)]

class SquareLoss(FunctionNode):
    """
    Inputs: [a, b]
        a represents a matrix of size (batch_size x dim)
        b must have the same shape as a
    Output: a number

    This node first computes 0.5 * (a[i,j] - b[i,j])**2 at all positions (i,j)
    in the inputs, which creates a (batch_size x dim) matrix. It then calculates
    and returns the mean of all elements in this matrix.
    """

    @staticmethod
    def forward(inputs):
        assert len(inputs) == 2

        return np.mean( 0.5 * np.square(np.subtract(inputs[0], inputs[1])) )

    @staticmethod
    def backward(inputs, gradient):
        assert len(inputs) == 2

        val = np.subtract(inputs[0], inputs[1])
        val *= (gradient / val.size)
        return [val, -1*val]

class SoftmaxLoss(FunctionNode):
    """
    A batched softmax loss, used for classification problems.

    IMPORTANT: do not swap the order of the inputs to this node!

    Inputs: [logits, labels]
        logits: a (batch_size x num_classes) matrix of scores, that is typically
            calculated based on previous layers. Each score can be an arbitrary
            real number.
        labels: a (batch_size x num_classes) matrix that encodes the correct
            labels for the examples. All entries must be non-negative and the
            sum of values along each row should be 1.
    Output: a number

    We have provided the complete implementation for your convenience.
    """
    @staticmethod
    def softmax(input):
        exp = np.exp(input - np.max(input, axis=1, keepdims=True))
        return exp / np.sum(exp, axis=1, keepdims=True)

    @staticmethod
    def forward(inputs):
        softmax = SoftmaxLoss.softmax(inputs[0])
        labels = inputs[1]
        assert np.all(labels >= 0), \
            "Labels input to SoftmaxLoss must be non-negative. (Did you pass the inputs in the right order?)"
        assert np.allclose(np.sum(labels, axis=1), np.ones(labels.shape[0])), \
            "Labels input to SoftmaxLoss do not sum to 1 along each row. (Did you pass the inputs in the right order?)"

        return np.mean(-np.sum(labels * np.log(softmax), axis=1))

    @staticmethod
    def backward(inputs, gradient):
        softmax = SoftmaxLoss.softmax(inputs[0])
        return [
            gradient * (softmax - inputs[1]) / inputs[0].shape[0],
            gradient * (-np.log(softmax)) / inputs[0].shape[0]
        ]

if __name__ == '__main__':
    main()
