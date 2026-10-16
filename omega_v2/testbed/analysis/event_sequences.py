"""Query-side event automata; their flags never enter physical entropy."""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import expm_multiply


def ordered_event_probability(world, root, predicates, horizon, max_states=100000):
    """Probability of matching an ordered event subsequence by a deadline.

    Other events may occur between matches. Predicates apply to native events,
    not arbitrary labels split out of an aggregated transition matrix.
    """
    if not predicates or not np.isfinite(horizon) or horizon<0:
        raise ValueError('Nonempty sequence and finite nonnegative horizon required')
    n=len(world.states);stages=len(predicates)+1
    if n*stages>max_states:raise MemoryError('Analytical automaton state cap')
    index={s:i for i,s in enumerate(world.states)};rows=[];cols=[];rates=[]
    for stage in range(stages):
        for i,state in enumerate(world.states):
            source=stage*n+i;total=0.
            for module in world.modules:
                for event in module.events(state):
                    if not np.isfinite(event.rate) or event.rate<0:raise ValueError('Invalid native rate')
                    if event.rate==0:continue
                    next_stage=stage+int(stage<stages-1 and predicates[stage](event))
                    rows.append(source);cols.append(next_stage*n+index[event.target]);rates.append(event.rate)
                    total+=event.rate
            rows.append(source);cols.append(source);rates.append(-total)
    q=coo_matrix((rates,(rows,cols)),shape=(n*stages,n*stages)).tocsr()
    initial=np.zeros(n*stages);initial[index[root]]=1
    final=expm_multiply(q.T*horizon,initial)
    if abs(sum(final)-1)>1e-9 or min(final)<-1e-12:raise ArithmeticError('Automaton probability closure')
    return {'probability':float(final[(stages-1)*n:].sum()),'stages':stages,
            'analytical_states':n*stages,'physical_history_entropy_augmented':False}
