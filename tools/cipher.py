from langchain.chains import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate
from llm import llm
from graph import graph

CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about movies and provide recommendations.
Convert the user's question based on the schema.

Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
For movie titles that begin with "The", move "the" to the end, For example "The 39 Steps" becomes "39 Steps, The" or "The Matrix" becomes "Matrix, The".

If no data is returned, do not attempt to answer the question.
Only respond to questions that require you to construct a Cypher statement.
Do not include any explanations or apologies in your responses.

Examples:

Find movies and genres:
MATCH (m:Movie)-[:IN_GENRE]->(g)
RETURN m.title, g.name

(:Movie)-[:ACTED_IN]->(:Actor)
(:Movie)-[:DIRECTED_BY]->(:Director)
(:Movie)-[:IN_GENRE]->(:Genre)


Schema:
{schema}

Question:
{question}

Cypher Query:
"""

cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)
cypher_qa = GraphCypherQAChain.from_llm(
    llm,          # (1)
    graph=graph,  # (2)
    cypher_prompt=cypher_prompt

)

# Wrap the cypher_qa function
def cypher_qa_tool(input_str):
    print(f"Input to Cypher QA tool: {input_str}")
    try:
        response = cypher_qa({"query": input_str})
        print(f"Response from Cypher QA tool: {response}")

        # Check and print the query generated by the chain
        generated_query = response.get("query", "")
        print(f"Generated Cypher Query: {generated_query}")

        # Ensure the response is a string
        response_content = response.get("result", "")
        if not isinstance(response_content, str):
            response_content = str(response_content)

        if response_content == "I don't know the answer.":
            print("The tool couldn't find the answer. Verify the graph data and query format.")
        
        return response_content
    except Exception as e:
        print(f"Error in Cypher QA tool: {e}")
        return "An error occurred while processing your request."