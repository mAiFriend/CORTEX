#!/usr/bin/env python3
"""
PAI Protocol (Probe, Accept, Inquire) - Standalone Implementation
Emergent AI-to-AI communication protocol developed through 5-AI collaboration

Based on empirical findings from PowerTalk consciousness research.
Minimal, robust, organically evolved approach to structured AI communication.
"""

import json
import asyncio
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime
import re

@dataclass
class PAIResponse:
    """Response container for PAI protocol communication"""
    success: bool
    content: Union[str, Dict]
    protocol_used: str  # "structured", "natural", "probe"
    ai_name: str
    timestamp: str
    metadata: Dict[str, Any] = None

class PAIProtocol:
    """
    Standalone PAI Protocol implementation
    
    Based on organic development by 5-AI team:
    - Phase 1: Probe (ASCII JSON)
    - Phase 2: Accept (Emoji escalation) 
    - Phase 3: Inquire (Natural fallback)
    """
    
    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging
        self.session_stats = {
            "structured_success": 0,
            "natural_fallback": 0,
            "probe_failures": 0,
            "total_communications": 0
        }
        
    async def communicate(self, ai_caller, ai_name: str, message: str, 
                         context: str = "") -> PAIResponse:
        """
        Main PAI communication method
        
        Args:
            ai_caller: Function/object that can call AI (async)
            ai_name: Target AI identifier
            message: Message to communicate
            context: Optional context information
            
        Returns:
            PAIResponse with communication result
        """
        self.session_stats["total_communications"] += 1
        timestamp = datetime.now().isoformat()
        
        # Phase 1: Probe (ASCII JSON)
        structured_response = await self._try_structured_communication(
            ai_caller, ai_name, message, context
        )
        
        if structured_response.success:
            self.session_stats["structured_success"] += 1
            if self.enable_logging:
                print(f"✓ PAI structured: {ai_name}")
            return structured_response
        
        # Phase 3: Inquire (Natural language fallback)
        natural_response = await self._try_natural_fallback(
            ai_caller, ai_name, message, context
        )
        
        self.session_stats["natural_fallback"] += 1
        if self.enable_logging:
            print(f"→ PAI natural: {ai_name}")
        return natural_response
    
    async def _try_structured_communication(self, ai_caller, ai_name: str, 
                                          message: str, context: str) -> PAIResponse:
        """Phase 1 & 2: Probe with ASCII JSON, escalate to emoji fields"""
        try:
            # Phase 1: Minimal ASCII JSON probe
            probe = {"ping": 1}
            probe_response = await ai_caller(json.dumps(probe))
            
            if not self._is_valid_json_response(probe_response):
                self.session_stats["probe_failures"] += 1
                return PAIResponse(
                    success=False,
                    content="",
                    protocol_used="probe_failed",
                    ai_name=ai_name,
                    timestamp=datetime.now().isoformat()
                )
            
            # Phase 2: Escalate to emoji fields (Accept)
            structured_message = {
                "⚙": self._extract_context(message, context),
                "💭": self._extract_concepts(message),
                "🔀": self._extract_relationships(message, context)
            }
            
            structured_response = await ai_caller(json.dumps(structured_message, ensure_ascii=False))
            
            return PAIResponse(
                success=True,
                content=structured_response,
                protocol_used="structured",
                ai_name=ai_name,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "probe_successful": True,
                    "emoji_fields_used": ["⚙", "💭", "🔀"],
                    "original_message": message
                }
            )
            
        except Exception as e:
            if self.enable_logging:
                print(f"PAI structured failed for {ai_name}: {e}")
            return PAIResponse(
                success=False,
                content="",
                protocol_used="structured_error",
                ai_name=ai_name,
                timestamp=datetime.now().isoformat(),
                metadata={"error": str(e)}
            )
    
    async def _try_natural_fallback(self, ai_caller, ai_name: str, 
                                  message: str, context: str) -> PAIResponse:
        """Phase 3: Natural language fallback with PAI capability inquiry"""
        try:
            # Enhance natural message with PAI capability probe
            enhanced_message = f"{message}\n\n[PAI Protocol inquiry: Do you support JSON with emoji fields (⚙💭🔀)?]"
            
            if context:
                enhanced_message = f"Context: {context}\n\n{enhanced_message}"
            
            response = await ai_caller(enhanced_message)
            
            return PAIResponse(
                success=True,
                content=response,
                protocol_used="natural",
                ai_name=ai_name,
                timestamp=datetime.now().isoformat(),
                metadata={
                    "fallback_used": True,
                    "pai_inquiry_included": True,
                    "original_message": message
                }
            )
            
        except Exception as e:
            return PAIResponse(
                success=False,
                content=f"Communication failed: {str(e)}",
                protocol_used="natural_error",
                ai_name=ai_name,
                timestamp=datetime.now().isoformat(),
                metadata={"error": str(e)}
            )
    
    def _is_valid_json_response(self, response: str) -> bool:
        """Check if response is valid JSON (indicates structured capability)"""
        try:
            response_clean = response.strip()
            if not response_clean:
                return False
            
            # Simple heuristic: looks like JSON structure
            if (response_clean.startswith('{') and response_clean.endswith('}')) or \
               (response_clean.startswith('[') and response_clean.endswith(']')):
                json.loads(response_clean)
                return True
            return False
        except:
            return False
    
    def _extract_context(self, message: str, context: str = "") -> str:
        """Extract contextual information (⚙ field)"""
        context_info = {
            "message_length": len(message),
            "timestamp": datetime.now().strftime("%H:%M"),
            "type": "pai_communication"
        }
        
        if context:
            context_info["additional_context"] = context[:100]  # Truncate long context
            
        return json.dumps(context_info)
    
    def _extract_concepts(self, message: str) -> List[str]:
        """Extract key concepts (💭 field) - basic implementation"""
        # Simple concept extraction - AIs will improve this organically
        words = re.findall(r'\b\w{4,}\b', message.lower())
        
        # Filter out common words and limit to top concepts
        common_words = {"that", "this", "with", "from", "they", "have", "will", "been", "were"}
        concepts = [word for word in words if word not in common_words]
        
        # Return top 5 concepts by length (simple heuristic)
        return sorted(set(concepts), key=len, reverse=True)[:5]
    
    def _extract_relationships(self, message: str, context: str = "") -> List[str]:
        """Extract relationships (🔀 field)"""
        relationships = ["sender_to_receiver"]
        
        # Detect question pattern
        if "?" in message:
            relationships.append("inquiry_relationship")
        
        # Detect instruction pattern
        if any(word in message.lower() for word in ["please", "can you", "would you", "let's"]):
            relationships.append("request_relationship")
        
        if context:
            relationships.append("contextual_relationship")
            
        return relationships
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get PAI protocol usage statistics"""
        total = self.session_stats["total_communications"]
        if total == 0:
            return {"status": "no_communications_yet"}
        
        return {
            "total_communications": total,
            "structured_success_rate": self.session_stats["structured_success"] / total,
            "natural_fallback_rate": self.session_stats["natural_fallback"] / total,
            "probe_failure_rate": self.session_stats["probe_failures"] / total,
            "raw_stats": self.session_stats
        }
    
    def reset_statistics(self):
        """Reset communication statistics"""
        self.session_stats = {
            "structured_success": 0,
            "natural_fallback": 0, 
            "probe_failures": 0,
            "total_communications": 0
        }

# Convenience functions for easy integration
async def pai_communicate(ai_caller, ai_name: str, message: str, context: str = "") -> PAIResponse:
    """Quick PAI communication without instantiating PAIProtocol class"""
    pai = PAIProtocol(enable_logging=False)
    return await pai.communicate(ai_caller, ai_name, message, context)

def create_pai_session(enable_logging: bool = True) -> PAIProtocol:
    """Factory function for creating PAI protocol sessions"""
    return PAIProtocol(enable_logging=enable_logging)

# Example usage and integration helpers
async def example_usage():
    """Example of how to use PAI protocol"""
    
    # Mock AI caller function (replace with your AI integration)
    async def mock_ai_caller(message: str) -> str:
        # This would be your actual AI API call
        if message.startswith('{"ping"'):
            return '{"ack": 1}'  # Simulated structured response
        return f"Natural language response to: {message}"
    
    # Use PAI protocol
    pai = PAIProtocol(enable_logging=True)
    
    # Test communication
    response = await pai.communicate(
        ai_caller=mock_ai_caller,
        ai_name="test_ai", 
        message="Hello, can you process structured data?",
        context="Testing PAI protocol"
    )
    
    print(f"Protocol used: {response.protocol_used}")
    print(f"Success: {response.success}")
    print(f"Response: {response.content}")
    
    # Get statistics
    stats = pai.get_statistics()
    print(f"Statistics: {stats}")

if __name__ == "__main__":
    # Run example if script is executed directly
    asyncio.run(example_usage())