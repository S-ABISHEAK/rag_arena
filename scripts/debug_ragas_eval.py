from src.retrieval.traditional_rag import TraditionalRAG
from src.evaluation.ragas_evaluator import RagasEvaluator

r = TraditionalRAG()
resp = r.query('What is AI-enabled security analytics?')
contexts = [d.page_content for d in resp['sources']]

print('answer length', len(resp['answer']))
print('num contexts', len(contexts))

res = RagasEvaluator.evaluate_response(resp['question'], resp['answer'], contexts)

import json
print('RESULT:')
print(json.dumps(res, indent=2))
