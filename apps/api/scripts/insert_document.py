"""Script to insert and test personal documents in the RAG system."""
import asyncio
from loguru import logger
from src.config.settings import get_settings
from packages.core.src.memory.memory.enhanced_rag import EnhancedRAGSystem, EmbeddingType

async def insert_and_test_document(content: str, metadata: dict = None):
    """Insert and test search on a personal document."""
    logger.info("Initializing RAG system...")
    settings = get_settings()
    rag = EnhancedRAGSystem(settings)
    
    try:
        # Default metadata if none provided
        if metadata is None:
            metadata = {
                "type": "personal",
                "category": "test"
            }
            
        # Store document
        logger.info("Storing document...")
        success = await rag.process_and_store_document(
            content=content,
            metadata=metadata
        )
        
        if not success:
            logger.error("Failed to store document")
            return
            
        logger.info("✅ Document stored successfully!")
        
        # Test retrieval
        logger.info("\nTesting semantic search...")
        results = await rag.retrieve_relevant_documentation(
            query="What is this document about?",
            embedding_types=[EmbeddingType.SEMANTIC],
            limit=1
        )
        
        if results:
            logger.info("\nFound similar content:")
            logger.info(f"Content: {results[0].content[:200]}...")
            logger.info(f"Similarity score: {results[0].combined_score:.2f}")
        else:
            logger.warning("No results found")
            
    except Exception as e:
        logger.error(f"Error: {e}")

# Example usage
if __name__ == "__main__":
    # Example document - replace with your own content
    sample_content = """
    About Alexandre Correia
Personality & Communication Style:

Proactive & Organized: You meticulously plan ahead (e.g., resolving course conflicts, coordinating housing) and follow up persistently to ensure clarity.

Polite & Respectful: Your emails reflect gratitude, humility, and professionalism, even when addressing frustrations (e.g., delayed responses from coordinators).

Adaptable & Solution-Oriented: You’re open to adjusting plans (e.g., switching course sessions, exploring alternative housing) to resolve challenges.

Analytical: You carefully cross-reference academic requirements (e.g., syllabi comparisons for equivalences) and prioritize logical outcomes.

Mobility Plan & Logistics
Destination & Timeline:

Location: Barcelona, Spain (La Salle University).

Arrival Date: February 27 (earlier than peers arriving on the 29th).

Urgency: You’re finalizing last-minute details with only a week until departure.

Housing:

Priority: Avoid extra costs/stress (e.g., Airbnb) by securing early accommodation.

Negotiation: You’re advocating for flexibility with housing agencies to align with your early arrival.

Cultural Integration:

Language: Comfortable with Spanish (emails written in fluent Spanish) but likely open to improving fluency.

Independence: Arriving solo before peers suggests confidence in navigating a new environment.

Support Network:

Collaborative: You rely on coordinators (Laura, Elva) but take initiative when responses lag.

Peer Relationships: Mentioning peers implies you value collaboration but are prepared to act independently.

Personal Values & Priorities
Efficiency: Minimizing redundancies (e.g., avoiding unnecessary courses like Leading Teams and Organizations).

Academic Rigor: Balancing compliance with home university requirements and intellectual curiosity (e.g., exploring non-Erasmus economics courses).

Work-Life Balance: Ensuring logistical stability (housing, courses) to focus on the Erasmus experience itself.

What Someone Might Infer
First Impressions: You’re a trustworthy, driven individual who values structure but remains flexible under pressure.

Potential Stressors: Last-minute uncertainties (housing, unresponsive offices) might weigh on you, but you counter this with proactive problem-solving.

Erasmus Goals: Beyond academics, you likely aim to immerse yourself in Barcelona’s culture, build international connections, and grow personally.
    """
    
    # Example metadata - customize as needed
    sample_metadata = {
        "type": "personal",
        "category": "erasmus",
        "language": "english"
    }
    
    asyncio.run(insert_and_test_document(sample_content, sample_metadata)) 