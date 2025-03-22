"""
Event Bus - Handles message publishing and subscription.
"""
import asyncio
import logging
from typing import Dict, List, Any, Callable, Awaitable, Optional
import uuid

logger = logging.getLogger(__name__)

# Type for event handlers: async functions that take an event and return nothing
EventHandler = Callable[[Dict[str, Any]], Awaitable[None]]

class EventBus:
    """
    Event Bus implementation for message publishing and subscription.
    This replaces the BizTalk MessageBox database in the architecture.
    """
    
    def __init__(self):
        self.subscribers: Dict[str, Dict[str, EventHandler]] = {}
        self.message_history: Dict[str, List[Dict[str, Any]]] = {}
        
    async def publish(self, topic: str, event: Dict[str, Any]) -> str:
        """
        Publish an event to a topic.
        
        Args:
            topic: The topic to publish to
            event: The event data to publish
            
        Returns:
            The event ID
        """
        # Ensure the event has an ID
        if "event_id" not in event:
            event["event_id"] = str(uuid.uuid4())
            
        logger.info(f"Publishing event {event['event_id']} to topic {topic}")
        
        # Record the event in the message history
        if topic not in self.message_history:
            self.message_history[topic] = []
            
        self.message_history[topic].append(event)
        
        # If there are subscribers for this topic, notify them
        if topic in self.subscribers:
            subscriber_tasks = []
            for subscriber_id, handler in self.subscribers[topic].items():
                logger.debug(f"Notifying subscriber {subscriber_id} of event {event['event_id']}")
                subscriber_tasks.append(self._notify_subscriber(subscriber_id, handler, event))
                
            # Wait for all subscriber notifications to complete
            if subscriber_tasks:
                await asyncio.gather(*subscriber_tasks)
                
        return event["event_id"]
        
    async def _notify_subscriber(self, subscriber_id: str, handler: EventHandler, event: Dict[str, Any]) -> None:
        """
        Notify a subscriber of an event.
        
        Args:
            subscriber_id: The ID of the subscriber
            handler: The subscriber's event handler
            event: The event to notify about
        """
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error notifying subscriber {subscriber_id}: {str(e)}")
            
    def subscribe(self, topic: str, handler: EventHandler, subscriber_id: Optional[str] = None) -> str:
        """
        Subscribe to a topic.
        
        Args:
            topic: The topic to subscribe to
            handler: The event handler to call when an event is published to the topic
            subscriber_id: Optional subscriber ID, if not provided one will be generated
            
        Returns:
            The subscriber ID
        """
        # Generate a subscriber ID if one wasn't provided
        if subscriber_id is None:
            subscriber_id = str(uuid.uuid4())
            
        # Create the topic if it doesn't exist
        if topic not in self.subscribers:
            self.subscribers[topic] = {}
            
        # Add the subscriber
        self.subscribers[topic][subscriber_id] = handler
        
        logger.info(f"Subscriber {subscriber_id} subscribed to topic {topic}")
        
        return subscriber_id
        
    def unsubscribe(self, topic: str, subscriber_id: str) -> bool:
        """
        Unsubscribe from a topic.
        
        Args:
            topic: The topic to unsubscribe from
            subscriber_id: The subscriber ID to unsubscribe
            
        Returns:
            True if the subscriber was unsubscribed, False otherwise
        """
        if topic not in self.subscribers or subscriber_id not in self.subscribers[topic]:
            logger.warning(f"Subscriber {subscriber_id} not found for topic {topic}")
            return False
            
        # Remove the subscriber
        del self.subscribers[topic][subscriber_id]
        
        # Remove the topic if there are no more subscribers
        if not self.subscribers[topic]:
            del self.subscribers[topic]
            
        logger.info(f"Subscriber {subscriber_id} unsubscribed from topic {topic}")
        
        return True
        
    def get_topic_history(self, topic: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the message history for a topic.
        
        Args:
            topic: The topic to get the history for
            limit: The maximum number of messages to return
            
        Returns:
            List of events published to the topic, most recent first
        """
        if topic not in self.message_history:
            return []
            
        return list(reversed(self.message_history[topic][-limit:]))
        
    def clear_history(self, topic: Optional[str] = None) -> None:
        """
        Clear the message history for a topic, or all topics if none specified.
        
        Args:
            topic: Optional topic to clear the history for
        """
        if topic is None:
            self.message_history = {}
            logger.info("Cleared all message history")
        elif topic in self.message_history:
            self.message_history[topic] = []
            logger.info(f"Cleared message history for topic {topic}")
            
class KafkaEventBus(EventBus):
    """
    Kafka implementation of the EventBus.
    For production use, this would be implemented with a real Kafka client.
    """
    
    def __init__(self, bootstrap_servers: str):
        super().__init__()
        self.bootstrap_servers = bootstrap_servers
        logger.info(f"Initialized Kafka event bus with bootstrap servers: {bootstrap_servers}")
        
    async def publish(self, topic: str, event: Dict[str, Any]) -> str:
        """
        Publish an event to a Kafka topic.
        
        Args:
            topic: The topic to publish to
            event: The event data to publish
            
        Returns:
            The event ID
        """
        # In a real implementation, this would publish to a Kafka topic
        # For now, just use the in-memory implementation
        return await super().publish(topic, event)
        
    def subscribe(self, topic: str, handler: EventHandler, subscriber_id: Optional[str] = None) -> str:
        """
        Subscribe to a Kafka topic.
        
        Args:
            topic: The topic to subscribe to
            handler: The event handler to call when an event is published to the topic
            subscriber_id: Optional subscriber ID, if not provided one will be generated
            
        Returns:
            The subscriber ID
        """
        # In a real implementation, this would subscribe to a Kafka topic
        # For now, just use the in-memory implementation
        return super().subscribe(topic, handler, subscriber_id)
        
class AzureServiceBusEventBus(EventBus):
    """
    Azure Service Bus implementation of the EventBus.
    For production use, this would be implemented with a real Azure Service Bus client.
    """
    
    def __init__(self, connection_string: str):
        super().__init__()
        self.connection_string = connection_string
        logger.info("Initialized Azure Service Bus event bus")
        
    async def publish(self, topic: str, event: Dict[str, Any]) -> str:
        """
        Publish an event to an Azure Service Bus topic.
        
        Args:
            topic: The topic to publish to
            event: The event data to publish
            
        Returns:
            The event ID
        """
        # In a real implementation, this would publish to an Azure Service Bus topic
        # For now, just use the in-memory implementation
        return await super().publish(topic, event)
        
    def subscribe(self, topic: str, handler: EventHandler, subscriber_id: Optional[str] = None) -> str:
        """
        Subscribe to an Azure Service Bus topic.
        
        Args:
            topic: The topic to subscribe to
            handler: The event handler to call when an event is published to the topic
            subscriber_id: Optional subscriber ID, if not provided one will be generated
            
        Returns:
            The subscriber ID
        """
        # In a real implementation, this would subscribe to an Azure Service Bus topic
        # For now, just use the in-memory implementation
        return super().subscribe(topic, handler, subscriber_id) 