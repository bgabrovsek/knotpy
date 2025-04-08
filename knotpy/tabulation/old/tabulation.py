class InvariantPartitionTable(dict):
    """
    A data structure that inherits from dict, designed to organize diagrams into partitions based on tuples of invariant
    values. Each key in the dictionary is a tuple representing the invariants, and the value is a list of knots that
    share these invariants.
    """

    def __init__(self, invariants):
        """
        Initializes the KnotPartitionTable possibly with pre-defined data.

        :param invariants: Optional dictionary with tuples of invariants as keys and lists of knots as values.
        :type invariants: dict
        """
        if isinstance(invariants, dict):
            self.invariants = sorted(invariants.items(), key=lambda p: p[0])
        else:
            raise TypeError("Invariants should be given as dictionaries")

        super().__init__()

    def add(self, diagram):
        invariants = (func(diagram) for inv_name, func in self.invariants)
        if invariants not in super():
            super()[invariants] = {diagram, }
        else:
            super()[invariants].add(diagram)

    def __repr__(self):
        """
        String representation for debugging that shows the table structure.
        """
        return f"KnotPartitionTable({super().__repr__()})"