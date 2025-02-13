import re
from presidio_analyzer import PatternRecognizer, Pattern, AnalyzerEngine
from presidio_anonymizer import  AnonymizerEngine
import logging
logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)

class Customregxpiidetectorandanonimizer: 
  def __init__(self,configobj) -> None:
      self.analyzer = AnalyzerEngine()
      self.anonymizer = AnonymizerEngine()
      self.score_threshold = configobj['score_threshold']
      self.language = configobj['language']
      self.allowedlist = configobj['targetlist']
      self.doanonymize = configobj.get('doanonymize', True)

  def customanalyzer(self, contextstr):
      try : 
          response = {}
          panalyzer = AnalyzerEngine()
          tuplist = tuple(self.allowedlist)
          #print(f"considering score threshold:{self.score_threshold}")
          allowedpattern = rf"\b({'|'.join(map(re.escape, tuplist))})\b" 
          keywordincludepattern = Pattern(
              name="keywordincludepattern",
              regex=allowedpattern, 
              score=self.score_threshold
          )
          cust_regex_recognizer = PatternRecognizer(
              supported_entity="keywordincludepattern",
              patterns=[keywordincludepattern]
          )
          panalyzer.registry.add_recognizer(cust_regex_recognizer)
          panonymizer = AnonymizerEngine()
          results = panalyzer.analyze(text=contextstr, language=self.language)

          #print(f"results are {results}")

          refined_results = [r for r in results if contextstr[r.start:r.end] not in tuplist]
          #print(f"refined results are {refined_results}")
   
          if self.doanonymize: 
              panonymizeresult= panonymizer.anonymize(text=contextstr,analyzer_results=refined_results)
              panonymizeresulttext = panonymizeresult.text
          else: 
              panonymizeresulttext = None 
          
          if refined_results:  
            response['textdetected'],response['entitiesdetected'], response['capturedentityscores'], response['Totalentityscores'] =[ ],[ ],[ ],0
            for entry in refined_results:
                response['textdetected'].append(contextstr[entry.start:entry.end])
                response['entitiesdetected'].append(entry.entity_type)
                response['capturedentityscores'].append(entry.score)
                response['Totalentityscores'] = round(sum(response['capturedentityscores']),3)
                response['anonimizedtext'] = panonymizeresulttext
                response['piidetected'] = True
                response['contextsupplied'] = contextstr
            return response
          else:
            response['piidetected'] = False
            response['contextsupplied'] = contextstr
            return response
      except Exception as e:
          return f"Encountered Error while detecting pii  please find error as {e}"
