from nltk.collocations import TrigramAssocMeasures
from nltk.collocations import TrigramCollocationFinder
from random import sample

def read_raw_data(file_name):
    f = open(file_name, 'r')
    raw_data = []
    for line in f:
        raw_data.append(line)
    f.close()
    return raw_data
    
def char_type(character):
    if character in '\n y':
        return character
    if character in "aeiou":
        return 'V'
    if character in "bdgvz":
        return 'SC'
    if character in "ptkfs":
        return 'NC'
    return 'C'
    
def char_with_type(character):
    return (character, char_type(character))
    
def generate_corpus(raw_names):
    corpus = [];
    for name in raw_names:
        corpus.append(char_with_type('\n'))
        for character in name:
            corpus.append(char_with_type(character))
        # corpus.extend(name)
        corpus.append(char_with_type('\n'))
    corpus.append(char_with_type('\n'))
    return corpus
    
def get_word_end_probabilites(names):
    names_count = len(names)
    letter_counts = {}
    for name in names:
        letter = name[-1:]
        if not letter_counts.has_key(letter):
            letter_counts[letter] = 0
        letter_counts[letter] = letter_counts[letter] + 1
        
    for key in letter_counts.keys():
        letter_counts[key] = (letter_counts[key] + 0.0) / names_count
        
    return letter_counts
    
# def vowel_count_probabilities(names):
#     total_letter_count = 1.0
#     vowel_count = 1.0
#     for name in names:
#         total_letter_count = total_letter_count + len(name)
#         for character in name:
#             if character in 'aoueiy':
#                 vowel_count = vowel_count + 1
#     return vowel_count / total_letter_count;
    
    
def calculate_name_len_probabilites(names):
    names_count = len(names)
    name_len_counts = {}
    for name in names:
        name_len = len(name)
        if not name_len_counts.has_key(name_len):
            name_len_counts[name_len] = 0
        name_len_counts[name_len] = name_len_counts[name_len] + 1
    for key in name_len_counts.keys():
        name_len_counts[key] = (name_len_counts[key] + 0.0) / names_count
    return name_len_counts
    
class NameGenderData:
    def __init__(self, raw_data, unisex_names):
        self.data = raw_data
        self.name_count = len(raw_data)
        sample_size = len(raw_data) / 10
        self.testing_set = set(sample(raw_data, sample_size))
        self.training_set = (set(raw_data) - self.testing_set) - unisex_names
        self.name_len_probabilities = calculate_name_len_probabilites(self.training_set);
        self.last_letter_probabilities = get_word_end_probabilites(self.training_set);
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
        trigram_score = data.colloc_finder.score_ngram(trigram_measures.raw_freq, char_with_type(name[i]), char_with_type(name[i + 1]), char_with_type(name[i + 2]))
        if trigram_score is None:
            score = score * data.base_frequency
        else:
            score = score * trigram_score

    name_len_score = 0
    if data.name_len_probabilities.has_key(len(name)):
        name_len_score = data.name_len_probabilities[len(name)]
    else:
        name_len_score = data.base_name_len_probability
    
    # last_letter_score = data.base_name_len_probability
    # if data.last_letter_probabilities.has_key(name[-1:]):
    #     last_letter_score = data.last_letter_probabilities[name[-1:]]
    
    return score * name_len_score * data.name_probability
    
def getNameGenderRatio(name):
    maleScore = getNameScore(name, male_name_data)
    femaleScore = getNameScore(name, female_name_data)
    # print 'Scores for ' + name
    # print 'male ' + str(maleScore)
    # print 'female ' + str(femaleScore)
    # print 'total ' + str(maleScore / (maleScore + femaleScore))
    # print '-------------------'
    return maleScore / (maleScore + femaleScore)
    
def train():
    global male_name_data, female_name_data
    
    male_names = set(read_raw_data('male.txt'))
    female_names = set(read_raw_data('female.txt'))

    unisex_names = male_names.intersection(female_names);

    male_name_data = NameGenderData(male_names, unisex_names)
    female_name_data = NameGenderData(female_names, unisex_names)

    total_name_count = len(male_name_data.training_set) + len(female_name_data.training_set)

    male_name_data.name_probability = (len(male_name_data.training_set) + 0.0) / total_name_count
    female_name_data.name_probability = (len(female_name_data.training_set) + 0.0) / total_name_count


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
    
def run():
    train()
    return test()

sum = 0
test_runs = 100
for i in range(test_runs):
    sum += run()
    print i
    
print sum / test_runs