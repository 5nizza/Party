def to_dot(smt_module):
    dotStr = "digraph g { \n"
    state_trans = smt_module.get_model()[0]
    for i in range(len(state_trans.state)):
        dotStr += state_trans.state[i] + " -> " + \
                  state_trans.new_state[i] + " [label= \"" + state_trans.input[i].replace("i_r == ", "") + "\"] \n";

    dotStr += "}"

    return dotStr