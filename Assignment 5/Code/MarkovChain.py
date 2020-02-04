from nltk.tokenize import RegexpTokenizer
import random
import sys
import os

arguments = sys.argv[1:-1]
author_directories = arguments[:int(len(arguments)/2)]
probability_files = arguments[int(len(arguments)/2):]
result = sys.argv[-1]


class MarkovChain(object):

    smooth_factor = 0.00000001

    def __init__(self, author_directories, probability_files, result_file, extra_credit):
        self.author_directories = author_directories
        self.probability_files = probability_files
        self.extra_credit = extra_credit
        self.result_file = result_file
        self.result_output = []
        self.tokenizer = RegexpTokenizer(r'\w+')
        self.models = []

        self.stopset = ['i', 'me', 'my', 'myself', 'we', 'our',
                        'ours', 'ourselves', 'you', 'your', 'yours',
                        'yourself', 'yourselves', 'he', 'him', 'his',
                        'himself', 'she', 'her', 'hers', 'herself', 'it',
                        'its', 'itself', 'they', 'them', 'their', 'theirs',
                        'themselves', 'what', 'which', 'who', 'whom', 'this',
                        'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were',
                        'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do',
                        'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
                        'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
                        'with', 'about', 'against', 'between', 'into', 'through', 'during',
                        'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
                        'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',
                        'then', 'once', 'here', 'there', 'when', 'where', 'why',
                        'how', 'all', 'any', 'both', 'each', 'few', 'more',
                        'most', 'other', 'some', 'such', 'no', 'nor',
                        'not', 'only', 'own', 'same', 'so', 'than',
                        'too', 'very', 's', 't', 'can', 'will',
                        'just', 'don', 'should', 'now']

        self._uni_gram_distributions = []
        self._bi_gram_distributions = []
        self._tri_gram_distributions = []
        self.all_sentences = []

        for i in range(len(self.author_directories)):

            self.author_directory = self.author_directories[i]
            self.probability_file = self.probability_files[i]
            self.sentences = []
            self.text = self.set_text()
            self.word_list = self.tokenizer.tokenize(self.text)
            self.word_list = [w.lower() for w in self.word_list if w.lower() not in self.stopset]

            self._uni_gram_distribution = {}
            self._bi_gram_distribution = {}
            self._tri_gram_distribution = {}

            self._set_uni_gram_distribution()
            self._set_bi_gram_distribution()
            self._set_tri_gram_distribution()

            self._uni_gram_distributions.append(self._uni_gram_distribution)
            self._bi_gram_distributions.append(self._bi_gram_distribution)
            self._tri_gram_distributions.append(self._tri_gram_distribution)

        for i in range(len(self.author_directories)):

            self.author_directory = self.author_directories[i]
            self.probability_file = self.probability_files[i]
            self.sentences = []
            self.text = self.set_text()
            self.word_list = self.tokenizer.tokenize(self.text)
            self.word_list = [w.lower() for w in self.word_list if w.lower() not in self.stopset]

            self._uni_gram_distribution = self.models[i][0]
            self._bi_gram_distribution = self.models[i][1]
            self._tri_gram_distribution = self.models[i][2]

            self.generate_sentences(i)
            self.all_sentences.append(self.sentences)
            self.generate_files(i)

    def _set_uni_gram_distribution(self):

        """
        Generates unigram distribution for the model.
        Calculates unigram probability distribution.
        :return: None
        """

        if "count" not in self._uni_gram_distribution:
            self._uni_gram_distribution["count"] = 0

        if "list" not in self._uni_gram_distribution:
            self._uni_gram_distribution["list"] = []

        if "words" not in self._uni_gram_distribution:
            self._uni_gram_distribution["words"] = {}

        if "total_probability" not in self._uni_gram_distribution:
            self._uni_gram_distribution["total_probability"] = 0

        for word in self.word_list:

            if word not in self._uni_gram_distribution["words"]:
                self._uni_gram_distribution["words"][word] = {"count": 0}

            self._uni_gram_distribution["words"][word]["count"] += 1

            self._uni_gram_distribution["count"] += 1
            self._uni_gram_distribution["list"].append(word)

        for word in self._uni_gram_distribution["words"]:
            self._uni_gram_distribution["words"][word]["probability"] = \
                self._uni_gram_distribution["words"][word]["count"] / self._uni_gram_distribution["count"]
            self._uni_gram_distribution["total_probability"] += self._uni_gram_distribution["words"][word]["probability"]

    def _set_bi_gram_distribution(self):

        """
        Set bi gram distribution for model
        :return: None
        """

        for i in range(len(self.word_list)-1):

            if self.word_list[i] not in self._bi_gram_distribution:
                self._bi_gram_distribution[self.word_list[i]] = {"count": 0, "words": {}, "list": []}

            if self.word_list[i+1] not in self._bi_gram_distribution[self.word_list[i]]["words"]:
                self._bi_gram_distribution[self.word_list[i]]["words"][self.word_list[i+1]] = {"count": 0}

            self._bi_gram_distribution[self.word_list[i]]["words"][self.word_list[i + 1]]["count"] += 1
            self._bi_gram_distribution[self.word_list[i]]["count"] += 1
            self._bi_gram_distribution[self.word_list[i]]["list"].append(
                self.word_list[i+1])

        for word in self._bi_gram_distribution:
            for inner_word in self._bi_gram_distribution[word]["words"]:

                self._bi_gram_distribution[word]["words"][inner_word]["probability"] = \
                    self._bi_gram_distribution[word]["words"][inner_word]["count"]/self._bi_gram_distribution[word]["count"]

    def _set_tri_gram_distribution(self):

        """
        Sets trigram distribution for the model
        :return: None
        """

        for i in range(len(self.word_list)-2):

            if (self.word_list[i],self.word_list[i+1]) not in self._tri_gram_distribution:
                self._tri_gram_distribution[(self.word_list[i],self.word_list[i+1])] = {"count": 0, "words": {}, "list":[]}

            if self.word_list[i + 2] not in self._tri_gram_distribution[(self.word_list[i],self.word_list[i+1])]["words"]:
                self._tri_gram_distribution[(self.word_list[i],self.word_list[i+1])]["words"][self.word_list[i + 2]] = {"count": 0}

            self._tri_gram_distribution[(self.word_list[i],self.word_list[i+1])]["words"][self.word_list[i + 2]]["count"] += 1
            self._tri_gram_distribution[(self.word_list[i],self.word_list[i+1])]["count"] += 1
            self._tri_gram_distribution[(self.word_list[i],self.word_list[i+1])]["list"].append(
                self.word_list[i + 2])

        for word in self._tri_gram_distribution:
            for inner_word in self._tri_gram_distribution[word]["words"]:
                self._tri_gram_distribution[word]["words"][inner_word]["probability"] = \
                    self._tri_gram_distribution[word]["words"][inner_word]["count"] / self._tri_gram_distribution[word][
                        "count"]
        self.models.append([self._uni_gram_distribution, self._bi_gram_distribution, self._tri_gram_distribution])

    def generate_sentences(self, i):

        """
        :param i: The model number for which the sentence has to be generated. Works for extra credit as well.
        :return: None
        """

        if extra_credit:

            if i == 0:
                j = 1
            else:
                j = 0

            uni_gram_distributions_other = self.models[j][0]
            bi_gram_distributions_other = self.models[j][1]
            tri_gram_distribution_other = self.models[j][2]

        sentence_count = 1

        while len(self.sentences) < 10:

            sentence = ""
            result_sentence = ""
            sentence_number = "Sentence {}".format(sentence_count)
            result_probabilities = []

            result_probabilities_other = []

            while True:
                uni_gram_word, probability = MarkovChain.weighted_choice(self._uni_gram_distribution)
                    #random.choice(self._uni_gram_distribution["list"])
                if uni_gram_word in self._bi_gram_distribution:
                    break

            result_sentence += "Unigram Probability for word [{}] is {}.\n\n".\
                format(uni_gram_word, self._uni_gram_distribution["words"][uni_gram_word]["probability"])

            result_probabilities.append(self._uni_gram_distribution["words"][uni_gram_word]["probability"])

            if extra_credit:
                try:
                    result_probabilities_other.append(uni_gram_distributions_other["words"][uni_gram_word]["probability"])
                except:
                    result_probabilities_other.append(MarkovChain.smooth_factor)

            sentence += uni_gram_word + " "
            bi_gram_word = random.choice(self._bi_gram_distribution[uni_gram_word]["list"])

            result_sentence += "Bigram probability for word [{}] given first word from unigram [{}] is {}.\n\n".\
                format(bi_gram_word, uni_gram_word,
                       self._bi_gram_distribution[uni_gram_word]["words"][bi_gram_word]["probability"])

            result_probabilities.append(self._bi_gram_distribution[uni_gram_word]["words"][bi_gram_word]["probability"])

            if extra_credit:
                try:
                    result_probabilities_other.append(
                        bi_gram_distributions_other[uni_gram_word]["words"][bi_gram_word]["probability"])
                except:
                    result_probabilities_other.append(MarkovChain.smooth_factor)

            sentence += bi_gram_word + " "

            cnt = 2

            tri_gram_word = (uni_gram_word, bi_gram_word)

            while cnt < 20:

                tri_gram_word_new = random.choice(self._tri_gram_distribution[tri_gram_word]["list"])

                result_sentence += "Trigram probability for word [{}] given words [{}] is {}.\n".\
                    format(tri_gram_word_new, tri_gram_word,
                           self._tri_gram_distribution[tri_gram_word]["words"][tri_gram_word_new]["probability"])

                result_probabilities.append(self._tri_gram_distribution[tri_gram_word]["words"][tri_gram_word_new]["probability"])

                if extra_credit:
                    try:
                        result_probabilities_other.append(
                            tri_gram_distribution_other[tri_gram_word]["words"][tri_gram_word_new]["probability"])
                    except:
                        result_probabilities_other.append(MarkovChain.smooth_factor)

                sentence += tri_gram_word_new + " "
                tri_gram_word = (tri_gram_word[1], tri_gram_word_new)
                cnt += 1

            probability_product = 1
            for probability in result_probabilities:
                probability_product *= probability

            probability_product_other = 1
            for probability in result_probabilities_other:
                probability_product_other *= probability

            self.sentences.append([sentence_number, sentence, result_sentence, " * ".join([str(res) for res in result_probabilities]) +
                                   " = {}".format(probability_product), " * ".join([str(res) for res in result_probabilities_other]) +
                                   " = {}".format(probability_product_other)])

            sentence_count += 1

    def generate_files(self, i):

        """
        :param i: Unused parameter, instead class attributes are used to check model under consideration.
        :return: None
        """

        import pprint
        pp = pprint.PrettyPrinter(indent=2)

        def generate_probability_files():

            output_string = ""
            output_string += "************ Author Directory **********************\n\n"
            output_string += "{}".format(self.author_directory)

            output_string += "\n\n************ Result File ***************************\n\n"
            output_string += "{}".format(self.result_file)

            output_string += "\n\n************ Understanding the unigram distribution *************\n\n"
            output_string += '''
            
                'thought': {'count': 553, 'probability': 0.0016726353231543542}
                
                'thought' is the word, which has occurred 553, 
                and it's probability of getting picked is 0.0016726353231543542\n\n'''

            output_string += "\n\n************ Understanding the bigram distribution *************\n\n"
            output_string += '''
            'absorbing': { 'count': 8,
                 'list': [ 'fascinating',
                           'interest',
                           'interest',
                           'centuries',
                           'conversation',
                           'subject',
                           'work',
                           'reading'],
                 'words': { 'centuries': {'count': 1, 'probability': 0.125},
                            'conversation': {'count': 1, 'probability': 0.125},
                            'fascinating': {'count': 1, 'probability': 0.125},
                            'interest': {'count': 2, 'probability': 0.25},
                            'reading': {'count': 1, 'probability': 0.125},
                            'subject': {'count': 1, 'probability': 0.125},
                            'work': {'count': 1, 'probability': 0.125}}}
                            
            "absorbing" is the unigram, and "words" key has all the second words of the bigram with their respective 
            probabilities.\n\n'''

            output_string += "\n\n************ Understanding the trigram distribution ************\n\n"
            output_string += '''  ('à', 'pie'): { 'count': 3,
                  'list': ['every', 'emerges', 'went'],
                  'words': { 'emerges': { 'count': 1,
                                          'probability': 0.3333333333333333},
                             'every': { 'count': 1,
                                        'probability': 0.3333333333333333},
                             'went': { 'count': 1,
                                       'probability': 0.3333333333333333}}}
                                       
                ('à', 'pie') --> Represents the bigram of the trigram.
                Dictionary "words" has the third words of the trigram with their respective probability distribution.
                "list" holds all the words occurring after bigram ('à', 'pie'), with repetition so that it is easy to 
                randomly pick the word, which takes care of the probability.\n\n'''

            output_string += "\n\n************ Unigram Distribution ******************\n"
            output_string += "\n1. Total word count: {}\n2. Total unique word count: {}, 3. Total Probability: {}\n" \
                             "4. Probability Distribution of Unigrams: {}\n5. Unigram List: {}\n\n".format(
                                self._uni_gram_distribution["count"], len(self._uni_gram_distribution["words"]),
                                self._uni_gram_distribution["total_probability"],
                                pprint.pformat(self._uni_gram_distribution["words"],indent=2),
                                self._uni_gram_distribution["list"])

            output_string += "\n*********************************************************"

            output_string += "\n********* Bigram Distribution *********************\n"
            output_string += "{}".format(pprint.pformat(self._bi_gram_distribution, indent=2))

            output_string += "\n********* Trigram Distribution ********************\n"
            output_string += "{}".format(pprint.pformat(self._tri_gram_distribution, indent=2))
            output_string += "\n\n************************* END ******************************"

            fp = open(self.probability_file, 'w')
            fp.write(output_string)
            fp.close()

        def generate_result_files():

            output_string = ""
            output_string += "************ Author Directory **********************\n\n"
            output_string += "{}".format(self.author_directory)

            for res in self.sentences:

                output_string += "\n\n************** {} result data ***********\n\n".format(res[0])
                output_string += "Sentence : {}\n".format(res[1])
                output_string += "Sentence Probability Distribution: \n\n{}\n".format(res[2])
                output_string += "Sentence Probability: {}\n".format(res[3])

                if self.extra_credit:
                    output_string += "Sentence Probability with other model: {}\n".format(res[4])

            fp = open(self.result_file, 'a')
            fp.write(output_string)
            fp.close()

        generate_probability_files()
        generate_result_files()

    def set_text(self):
        files = os.listdir(self.author_directory)
        text = ""
        for afile in files:
            fp = open(os.path.join(self.author_directory, afile))
            text += fp.read()
        return text

    @staticmethod
    def weighted_choice(unigram):

        """
        :param unigram: Select a random word from the given unigram, bigram, trigram
        :return:
        """

        seq, prob = [], []

        for key in unigram["words"]:
            seq.append(key)
            prob.append(unigram["words"][key]["probability"])

        random_value = random.randrange(0, 1)

        for i, ele in enumerate(seq):
            if random_value <= prob[i]:
                return ele, prob[i]
            random_value -= prob[i]


extra_credit = False

if len(probability_files) == 2:
    extra_credit = True

mo = MarkovChain(author_directories=author_directories,
                 probability_files=probability_files,
                 result_file=result,
                 extra_credit=extra_credit)
