import streamlit as st
from crewai import Crew, Process
from ChatBot.agent import ResearchCrewAgents
from ChatBot.tasks import ResearchCrewTasks
from pydantic import BaseModel
import time


class ResearchCrew:
    def __init__(self, inputs):
        self.inputs = inputs
        self.agents = ResearchCrewAgents()
        self.tasks = ResearchCrewTasks()

    def serialize_crew_output(self, crew_output):
        return {"output": crew_output}

    def run(self, is_discord=False):
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
        self.result = crew.kickoff(inputs=self.inputs)
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


def process_question(question: str, is_discord: bool = False):
    research_crew = ResearchCrew({"question": question})
    result = research_crew.run(is_discord)

    # Check if result["result"] is useful
    crew_output_raw = result.get("result", "")
    if not has_useful_information(crew_output_raw):
        return {
            "result": "I cannot find any relevant information on this topic",
            "links": [],
        }

    return result["result"]["output"].raw


def chatBot():
    st.title("💬 Wingzxel Bot")
    st.caption("🚀 A Streamlit chatbot powered by Wingzxel")
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "How can I help you?"}
        ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        # msg = prompt
        with st.spinner("Processing..."):
            msg = process_question(prompt)
            time.sleep(1)
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)
