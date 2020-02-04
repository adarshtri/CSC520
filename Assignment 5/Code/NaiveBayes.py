import json
import sys

train_file = sys.argv[1]
test_file = sys.argv[2]
model_file = sys.argv[3]
result_file = sys.argv[4]


class NaiveBayes(object):

    def __init__(self, train_file, test_file, model_file, result_file):

        self.train_file = train_file
        self.test_file = test_file
        self.model_file = model_file
        self.result_file = result_file
        self.real_vs_prediction = []
        self.probability_model, self.result_model = NaiveBayes.convert_to_usable_format(self.train_file)
        self.predict_test(file=self.test_file)
        self.generate_data_file()

    def generate_data_file(self):

        match_count = 0
        confusion_matrix = [[0, 0], [0, 0]]

        for row in self.real_vs_prediction:
            if int(row[0]) == row[1]:
                match_count += 1

            confusion_matrix[int(row[0])][row[1]] += 1

        model_string = ""

        model_string += "************Files********************\n"
        model_string += "\nTraining file \"{}\".\nTesting file \"{}\".\nModel file \"{}\".\nResult file \"{}\".\n".format(
            self.train_file, self.test_file, self.model_file, self.result_file)

        prediction_accuracy = (match_count/len(self.real_vs_prediction))*100

        model_string += "\n***************Model*****************\n"
        model_string += "\nRepresentation explanation: The model is represented using a nested dictionary,\n" \
                        "where every key represents a field number. Within each field, every key in the nested\n" \
                        "dictionary holds possible class value. Within each class dictionary, the sub\n" \
                        "dictionary holds possible field values and the value of this key represents the\n" \
                        "conditional probability of the feature value given the class it is inside the\n" \
                        "representation.\n"

        model_string += '''
For example, sample key value pair from the model is give below,

    --> column number    "0": {
           --> class value "1": {
                                    "1": 0.46745562130177515,  --> this value implies P(1|1) for field 1.
                                    "0": 0.5325443786982249    --> this value implies P(0|1) for field 1. (Here 0 is the feature value and 1 is the class value.
                                },
           --> class value "0": {
                                    "1": 0.22727272727272727, --> this value implies P(1|0) for field 1.
                                    "0": 0.7727272727272727   --> this value implies p(0|0) for field 1.
                                }
                            }\n
                            
The above example represents one of the model nodes. Basically represents probability table for field 1.
'''

        model_string += "\n=========Final Model==================\n\n"
        model_string += json.dumps(self.probability_model, indent=4)

        model_fp = open(self.model_file, 'w')
        model_fp.write(model_string)
        model_fp.close()

        model_string = ""

        model_string += "************Files********************\n"
        model_string += "\nTraining file \"{}\".\nTesting file \"{}\".\nModel file \"{}\".\nResult file \"{}\".\n".format(
            self.train_file, self.test_file, self.model_file, self.result_file)

        prediction_accuracy = (match_count / len(self.real_vs_prediction)) * 100

        model_string += "\n**********Accuracy************************\n"

        model_string += "\nPrediction accuracy {}%.\n".format(round(prediction_accuracy, 2))

        model_string += "\n**********Confusion Matrix***************\n"

        model_string += "\nTrue Negatives : {}\nTrue Positives : {}\nFalse Negatives : {}\nFalse Positives : {}\n".format(
            confusion_matrix[0][0], confusion_matrix[1][1], confusion_matrix[1][0], confusion_matrix[0][1])

        model_string += "\n\n********* Row wise actual vs prediction *************\n"
        model_string += "\n*********** Correct Predictions ***********************\n"

        wrong_string = ""

        for res in self.real_vs_prediction:
            if int(res[0]) == res[1]:
                model_string += "\n{}\t{} (actual class)\t{} (prediction class)".format(", ".join(res[2]), res[0], res[1])
            else:
                wrong_string += "\n{}\t{} (actual class)\t{} (prediction class)".format(", ".join(res[2]), res[0],
                                                                                        res[1])

        model_string += "\n\n*********** Wrong Predictions ***********************\n"

        model_string += wrong_string

        model_fp = open(self.result_file, 'w')
        model_fp.write(model_string)
        model_fp.close()

    @staticmethod
    def convert_to_usable_format(file):

        probability_model = {}
        result_model = [0, 0]

        with open(file=file, mode='r') as fp:
            for cnt, line in enumerate(fp):
                if cnt == 0:
                    continue

                line = line.strip()
                fields = line.split(",")
                row_class = fields[-1][0]
                result_model[int(row_class)] += 1
                fields = fields[:-1]

                for field_number, field_value in enumerate(fields):

                    if field_number not in probability_model:
                        probability_model[field_number] = {}

                    if row_class not in probability_model[field_number]:
                        probability_model[field_number][row_class] = {}

                    if field_value not in probability_model[field_number][row_class]:
                        probability_model[field_number][row_class][field_value] = 0

                    probability_model[field_number][row_class][field_value] += 1

        for field_number in probability_model:
            for row_class in probability_model[field_number]:
                for field_value in probability_model[field_number][row_class]:
                    probability_model[field_number][row_class][field_value] /= result_model[int(row_class)]

        return probability_model, result_model

    def predict_test(self, file):

        with open(file=file, mode='r') as fp:
            for cnt, line in enumerate(fp):

                if cnt == 0:
                    continue

                line = line.strip()
                line = line.split(",")
                result = line[-1]
                line = line[:-1]

                self.real_vs_prediction.append([result, self.predict(line), line])

    def predict(self, prediction_row):

        probability_classes = [1]*len(self.result_model)

        for class_value, value in enumerate(self.result_model):
            for field_number, field_value in enumerate(prediction_row):
                try:
                    probability_classes[class_value] *= \
                        self.probability_model[field_number][str(class_value)][field_value]
                except KeyError as e:
                    probability_classes[class_value] *= 0

        probability_classes_sum = sum(probability_classes)
        probability_classes = [x/probability_classes_sum for x in probability_classes]

        return probability_classes.index(max(probability_classes))


nb = NaiveBayes(train_file=train_file,
                test_file=test_file,
                model_file=model_file,
                result_file=result_file)
