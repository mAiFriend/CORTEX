#!/bin/bash

echo "=== LOKALE AI-VERFÜGBARKEITS-CHECK ==="
echo "Teste neue Modelle für enhanced_6api.py Integration"
echo ""

# Check if Ollama is running
echo "1. Ollama Service Status:"
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama läuft auf localhost:11434"
else
    echo "❌ Ollama nicht erreichbar. Starte mit: ollama serve"
    exit 1
fi

echo ""
echo "2. Verfügbare Modelle:"
curl -s http://localhost:11434/api/tags | jq -r '.models[] | .name' | sort

echo ""
echo "3. Test der neuen Ziel-Modelle:"

# Test deepseek-coder-v2:16b
echo "Testing deepseek-coder-v2:16b..."
if ollama list | grep -q "deepseek-coder-v2:16b"; then
    echo "✅ deepseek-coder-v2:16b verfügbar"
    # Quick test
    echo '{"model": "deepseek-coder-v2:16b", "prompt": "Hello, test response", "stream": false}' | curl -s -X POST http://localhost:11434/api/generate -d @- | jq -r '.response' | head -c 100
    echo "..."
else
    echo "❌ deepseek-coder-v2:16b nicht gefunden. Installiere mit: ollama pull deepseek-coder-v2:16b"
fi

echo ""
# Test codellama:13b
echo "Testing codellama:13b..."
if ollama list | grep -q "codellama:13b"; then
    echo "✅ codellama:13b verfügbar"
    echo '{"model": "codellama:13b", "prompt": "Hello, test response", "stream": false}' | curl -s -X POST http://localhost:11434/api/generate -d @- | jq -r '.response' | head -c 100
    echo "..."
else
    echo "❌ codellama:13b nicht gefunden. Installiere mit: ollama pull codellama:13b"
fi

echo ""
# Test gemma2:9b (updated model name)
echo "Testing gemma3:12b..."
if ollama list | grep -q "gemma3:12b"; then
    echo "✅ gemma2:9b verfügbar"
    echo '{"model": "gemma3:12b", "prompt": "Hello, test response", "stream": false}' | curl -s -X POST http://localhost:11434/api/generate -d @- | jq -r '.response' | head -c 100
    echo "..."
else
    echo "❌ gemma3:12b nicht gefunden. Installiere mit: ollama pull gemma2:9b"
fi

echo ""
echo "=== INSTALLATION COMMANDS ==="
echo "ollama pull deepseek-coder-v2:16b"
echo "ollama pull codellama:13b" 
echo "ollama pull gemma3:12b"

echo ""
echo "=== ARCHETYPE ASSIGNMENT VORSCHLAG ==="
echo "deepseek-coder-v2:16b → 'Advanced Code Architect'"
echo "codellama:13b → 'Meta Code Specialist'"
echo "gemma3:12b → 'Google Research Innovator'"