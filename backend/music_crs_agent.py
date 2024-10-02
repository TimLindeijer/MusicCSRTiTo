from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.dialogue_act import DialogueAct
from dialoguekit.core.utterance import Utterance
from dialoguekit.participant.agent import Agent
from dialoguekit.participant.participant import DialogueParticipant
import logging

logging.basicConfig(level=logging.INFO)  # Set the level to INFO
logger = logging.getLogger(__name__)  # Create a logger
class MusicCRSAgent(Agent):
    def __init__(self, id: str):
        super().__init__(id)
        self.playlist = []

    def welcome(self) -> None:
        """Sends the agent's welcome message."""
        utterance = AnnotatedUtterance(
            "Hello! I'm MusicCRS. You can add, remove, view, or clear songs from your playlist. What would you like to do?",
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(utterance)

    def goodbye(self) -> None:
        utterance = AnnotatedUtterance(
            "It was nice talking to you. Bye!",
            dialogue_acts=[DialogueAct(intent=self.stop_intent)],
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(utterance)

    def receive_utterance(self, utterance: Utterance) -> None:
        """Handles user commands to manage the playlist."""
        user_input = utterance.text.lower()
        logger.info(f"utterance received {utterance}")
        

        if "add" in user_input:
            song = user_input.split("add")[-1].strip()
            self.playlist.append(song)
            response = f"Added '{song}' to your playlist."
        
        elif "remove" in user_input:
            song = user_input.split("remove")[-1].strip()
            if song in self.playlist:
                self.playlist.remove(song)
                response = f"Removed '{song}' from your playlist."
        elif "list" in user_input:
            response = "'"+"', '".join(self.playlist)+ "'"

        else:
            response = f"Message not understood."
        
        response = AnnotatedUtterance(
            "(MusicCRS) " + response,
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(response)
   
