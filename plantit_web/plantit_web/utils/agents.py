from plantit_web.agents.models import Agent


def has_virtual_memory(agent: Agent) -> bool:
    return agent.header_skip is not None and '--mem' in agent.header_skip


