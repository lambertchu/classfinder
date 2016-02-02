from gensim.models import Word2Vec

# ======= WORD2VEC ========

# To remove all punctuation and split into list:
# text.translate(None, string.punctuation).split()

# load descriptions from database
a = ['A', 'survey', 'of', 'the', 'scientific', 'study', 'of', 'human', 'nature', 'including', 'how', 'the', 'mind', 'works', 'and', 'how', 'the', 'brain', 'supports', 'the', 'mind', 'Topics', 'include', 'the', 'mental', 'and', 'neural', 'bases', 'of', 'perception', 'emotion', 'learning', 'memory', 'cognition', 'child', 'development', 'personality', 'psychopathology', 'and', 'social', 'interaction', 'Consideration', 'of', 'how', 'such', 'knowledge', 'relates', 'to', 'debates', 'about', 'nature', 'and', 'nurture', 'free', 'will', 'consciousness', 'human', 'differences', 'self', 'and', 'society']
b = ['An', 'integrated', 'introduction', 'to', 'electrical', 'engineering', 'and', 'computer', 'science', 'taught', 'using', 'substantial', 'laboratory', 'experiments', 'with', 'mobile', 'robots', 'Key', 'issues', 'in', 'the', 'design', 'of', 'engineered', 'artifacts', 'operating', 'in', 'the', 'natural', 'world', 'measuring', 'and', 'modeling', 'system', 'behaviors', 'assessing', 'errors', 'in', 'sensors', 'and', 'effectors', 'specifying', 'tasks', 'designing', 'solutions', 'based', 'on', 'analytical', 'and', 'computational', 'models', 'planning', 'executing', 'and', 'evaluating', 'experimental', 'tests', 'of', 'performance', 'refining', 'models', 'and', 'designs', 'Issues', 'addressed', 'in', 'the', 'context', 'of', 'computer', 'programs', 'control', 'systems', 'probabilistic', 'inference', 'problems', 'circuits', 'and', 'transducers', 'which', 'all', 'play', 'important', 'roles', 'in', 'achieving', 'robust', 'operation', 'of', 'a', 'large', 'variety', 'of', 'engineered', 'systems', '6', 'Engineering', 'Design', 'Points']
c = ['Introduces', 'classical', 'mechanics', 'Space', 'and', 'time', 'straightline', 'kinematics', 'motion', 'in', 'a', 'plane', 'forces', 'and', 'static', 'equilibrium', 'particle', 'dynamics', 'with', 'force', 'and', 'conservation', 'of', 'momentum', 'relative', 'inertial', 'frames', 'and', 'noninertial', 'force', 'work', 'potential', 'energy', 'and', 'conservation', 'of', 'energy', 'kinetic', 'theory', 'and', 'the', 'ideal', 'gas', 'rigid', 'bodies', 'and', 'rotational', 'dynamics', 'vibrational', 'motion', 'conservation', 'of', 'angular', 'momentum', 'central', 'force', 'motions', 'fluid', 'mechanics', 'Subject', 'taught', 'using', 'the', 'TEAL', 'TechnologyEnabled', 'Active', 'Learning', 'format', 'which', 'features', 'students', 'working', 'in', 'groups', 'of', 'three', 'discussing', 'concepts', 'solving', 'problems', 'and', 'doing', 'tabletop', 'experiments', 'with', 'the', 'aid', 'of', 'computer', 'data', 'acquisition', 'and', 'analysis']
d = ['Basic', 'principles', 'of', 'chemistry', 'and', 'their', 'application', 'to', 'engineering', 'systems', 'The', 'relationship', 'between', 'electronic', 'structure', 'chemical', 'bonding', 'and', 'atomic', 'order', 'Characterization', 'of', 'atomic', 'arrangements', 'in', 'crystalline', 'and', 'amorphous', 'solids', 'metals', 'ceramics', 'semiconductors', 'and', 'polymers', 'including', 'proteins', 'Topical', 'coverage', 'of', 'organic', 'chemistry', 'solution', 'chemistry', 'acidbase', 'equilibria', 'electrochemistry', 'biochemistry', 'chemical', 'kinetics', 'diffusion', 'and', 'phase', 'diagrams', 'Examples', 'from', 'industrial', 'practice', 'including', 'the', 'environmental', 'impact', 'of', 'chemical', 'processes', 'from', 'energy', 'generation', 'and', 'storage', 'eg', 'batteries', 'and', 'fuel', 'cells', 'and', 'from', 'emerging', 'technologies', 'eg', 'photonic', 'and', 'biomedical', 'devices']

# load model (very high overhead)
model = Word2Vec.load_word2vec_format('/Users/lambertchu/Documents/MIT/SuperUROP/NLP_Data/GoogleNews-vectors-negative300.bin', binary=True)

# remove all words not in the vocab of the model (to avoid key errors)
a = filter(lambda x: x in model.vocab, a)
b = filter(lambda x: x in model.vocab, b)
c = filter(lambda x: x in model.vocab, c)
d = filter(lambda x: x in model.vocab, d)

print model.n_similarity(a, ['psychology'])		# 9.00
print model.n_similarity(b, ['psychology'])		# 6.01
print model.n_similarity(c, ['psychology'])		# 8.01
print model.n_similarity(d, ['psychology'])		# 3.091