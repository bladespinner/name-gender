from nltk.collocations import TrigramAssocMeasures
from nltk.collocations import TrigramCollocationFinder
from random import sample

def read_raw_data(file_name):
    f = open(file_name, 'r')
    raw_data = []
    for line in f:
        raw_data.append(line)
    return raw_data
    
def generate_corpus(raw_names):
    corpus = [];
    for name in raw_names:
        corpus.append('\n')
        corpus.extend(name)
        corpus.append('\n')
    corpus.append('\n')
    return corpus
    
def calculate_name_len_probabilites(names):
    names_count = len(names)
    name_len_counts = {}
    for name in names:
        name_len = len(name)
        if not name_len_counts.has_key(name_len):
            name_len_counts[name_len] = 0;
        name_len_counts[name_len] = name_len_counts[name_len] + 1
    for key in name_len_counts.keys():
        name_len_counts[key] = (name_len_counts[key] + 0.0) / names_count;
    return name_len_counts;
    
class NameGenderData:
    def __init__(self, raw_data, unisex_names):
        self.data = raw_data
        self.name_count = len(raw_data)
        sample_size = len(raw_data) / 10
        self.testing_set = set(sample(raw_data, sample_size))
        self.training_set = (set(raw_data) - self.testing_set) - unisex_names
        self.name_len_probabilities = calculate_name_len_probabilites(self.training_set);
        self.base_name_len_probability = 1.0 / len(self.training_set);
        corpus = generate_corpus(self.training_set)
        invalid_trigram_count = self.name_count - 1
        self.trigram_count = len(corpus) - 2 - invalid_trigram_count
        self.base_frequency = 1.0 / self.trigram_count
        colloc_finder = TrigramCollocationFinder.from_words(corpus)
        colloc_finder.apply_freq_filter(3)
        colloc_finder.apply_ngram_filter(lambda w1, w2, w3: w1 == '\n' and w2 == '\n')
        self.colloc_finder = colloc_finder
        
def getNameScore(name, data):
    name = name + '\n'
    trigram_measures = TrigramAssocMeasures()
    name_len = len(name) - 2
    score = 1
    for i in range(0, name_len):
        trigram_score = data.colloc_finder.score_ngram(trigram_measures.raw_freq, name[i], name[i + 1], name[i + 2])
        if trigram_score is None:
            score = score * data.base_frequency
        else:
            score = score * trigram_score

    name_len_score = 0
    if data.name_len_probabilities.has_key(len(name)):
        name_len_score = data.name_len_probabilities[len(name)]
    else:
        name_len_score = data.base_name_len_probability
    
    return score * name_len_score * data.name_probability

male_names = set(read_raw_data('male.txt'))
female_names = set(read_raw_data('female.txt'))

unisex_names = male_names.intersection(female_names);

male_name_data = NameGenderData(male_names, unisex_names)
female_name_data = NameGenderData(female_names, unisex_names)

total_name_count = len(male_name_data.training_set) + len(female_name_data.training_set)

male_name_data.name_probability = (len(male_name_data.training_set) + 0.0) / total_name_count
female_name_data.name_probability = (len(female_name_data.training_set) + 0.0) / total_name_count
    
def getNameGenderRatio(name):
    maleScore = getNameScore(name, male_name_data)
    femaleScore = getNameScore(name, female_name_data)
    # print 'Scores for ' + name
    # print 'male ' + str(maleScore)
    # print 'female ' + str(femaleScore)
    # print 'total ' + str(maleScore / (maleScore + femaleScore))
    # print '-------------------'
    return maleScore / (maleScore + femaleScore)
    
def test():
    total_len = len(male_name_data.testing_set) + len(female_name_data.testing_set)
    guessed_len = 0.0;
    for name in male_name_data.testing_set:
        if getNameGenderRatio(name) >= 0.5:
            guessed_len = guessed_len + 1
    
    for name in female_name_data.testing_set:
        if getNameGenderRatio(name) < 0.5:
            guessed_len = guessed_len + 1
            
    return guessed_len / total_len
    
print test()