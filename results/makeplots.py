import matplotlib.pyplot as plt
import subprocess
import os
import re

def extract_recall(output):
    
    recalls = []
    for line in output.readlines():
        line = line.decode("utf-8")
        #print(line)
        elems = line.split()

        if elems[0].startswith("iprec_at_recall"):
            
            recalls.append(float(elems[2]))
        pass
    #print(recalls)
    return recalls

if __name__ == "__main__":

    for analyzer in ["baseline", "better"]:
        for sim in ["classic", "bm25"]:
            plt.figure()

            x = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

            results_filename = analyzer+"_"+sim+"_Longues_expanded.txt"
            lucene_filename =  analyzer+"_"+sim+"_longues.txt"
            exp_results     = subprocess.Popen(["trec_eval.exe", "qrels.1-50.AP8890.txt", results_filename], stdout=subprocess.PIPE, shell=True)
            lucene_results  = subprocess.Popen(["trec_eval.exe", "qrels.1-50.AP8890.txt", lucene_filename], stdout=subprocess.PIPE, shell=True)

            exp_results = exp_results.stdout
            lucene_results = lucene_results.stdout

            exp_results = extract_recall(exp_results)
            lucene_results = extract_recall(lucene_results)

            plt.plot(x, exp_results, 'r.-', x, lucene_results, 'b.-')
            plt.title("Precision-Recall for "+analyzer+"_"+sim+"_Longues")
            plt.xlabel("Recall")
            plt.ylabel("precision")

            plt.savefig("P-Rcurvefor"+analyzer+"_"+sim+"_Longues.png")
            plt.close

            #print(exp_results)

