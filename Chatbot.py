import streamlit as st
from crewai import Crew, Process
from ChatBot.agent import ResearchCrewAgents
from ChatBot.tasks import ResearchCrewTasks
from pydantic import BaseModel


class ResearchCrew:
    def __init__(self, inputs):
        self.inputs = inputs
        self.agents = ResearchCrewAgents()
        self.tasks = ResearchCrewTasks()

    def serialize_crew_output(self, crew_output):
        return {"output": crew_output}

    async def run(self, is_discord=False):
        from ChatBot.HybridSearch import hybrid_research

        researcher = self.agents.researcher()
        writer = self.agents.writer()

        research_task = self.tasks.research_task(researcher, self.inputs)
        writing_task = self.tasks.writing_task(writer, [research_task], self.inputs)

        crew = Crew(
            agents=[researcher, writer],
            tasks=[research_task, writing_task],
            process=Process.sequential,
            verbose=True,
        )
        self.result = await crew.kickoff_async(inputs=self.inputs)
        self.citation = hybrid_research(self.inputs, 5)[1]

        self.serialized_result = self.serialize_crew_output(self.result)
        return {"result": self.serialized_result, "links": self.citation}


class QuestionRequest(BaseModel):
    question: str


USELESS_INFO_PHRASES = [
    "I don't know",
    "does not contain information",
    "does not contain any information",
    "any information",
    "Unfortunately",
    "Agent stopped due to iteration limit or time limit",
]


def has_useful_information(result):
    return "Agent stopped due to iteration limit or time limit" not in result


async def ask_question(question: str):
    research_crew = ResearchCrew({"question": question})
    result = await research_crew.run()
    crew_output = result["result"]["output"]

    if has_useful_information(crew_output.raw):
        return result
    else:
        return "I cannot find any relevant information on this topic"


def chatBot():
    st.title("💬 Chatbot")
    st.caption("🚀 A Streamlit chatbot powered by OpenAI")
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "How can I help you?"}
        ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        msg = ask_question(prompt)
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)
