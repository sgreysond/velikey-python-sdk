# VeliKey Aegis Python SDK

[![PyPI version](https://badge.fury.io/py/velikey.svg)](https://badge.fury.io/py/velikey)
[![Python Support](https://img.shields.io/pypi/pyversions/velikey.svg)](https://pypi.org/project/velikey/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Quantum-safe crypto policy management for Python applications**

The VeliKey Python SDK provides a comprehensive interface for managing quantum-safe cryptographic policies, monitoring security posture, and automating compliance workflows.

## 🚀 Quick Start

### Installation

```bash
pip install velikey
```

### Basic Usage

```python
import asyncio
from velikey import AegisClient

async def main():
    # Initialize client
    client = AegisClient(api_key="your-api-key")
    
    # Quick setup for new customers
    setup = await client.quick_setup(
        compliance_framework="soc2",
        enforcement_mode="observe",
        post_quantum=True
    )
    print(f"✅ Created policy: {setup.policy_name}")
    
    # Monitor security status
    status = await client.get_security_status()
    print(f"🛡️ Health Score: {status.health_score}/100")
    
    # List and manage agents
    agents = await client.agents.list()
    print(f"🤖 Found {len(agents)} agents")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Synchronous Usage

```python
from velikey import AegisClientSync

# For non-async environments
client = AegisClientSync(api_key="your-api-key")

agents = client.agents.list()
print(f"Found {len(agents)} agents")

client.close()
```

## 📚 Core Features

### 🛡️ Policy Management

```python
# Create from compliance template
policy = await client.policies.create_from_template(
    template="soc2",
    enforcement_mode="enforce",
    post_quantum=True
)

# Custom policy builder
from velikey import PolicyBuilder

builder = PolicyBuilder()
policy_config = builder \
    .compliance_standard("Custom Security Policy") \
    .post_quantum_ready() \
    .enforcement_mode("enforce") \
    .build()

policy = await client.policies.create("My Policy", policy_config["rules"])

# Deploy to specific agents
await client.policies.deploy(policy.id, target_agents=["agent-1", "agent-2"])

# Rollback if needed
await client.policies.rollback(policy.id)
```

### 🤖 Agent Management

```python
# List all agents
agents = await client.agents.list()

# Get specific agent details
agent = await client.agents.get("agent-id")
print(f"Agent {agent.name} is {agent.status}")

# Trigger agent update
await client.agents.update(agent.id, version="1.2.0")

# Get deployment instructions
instructions = await client.agents.get_deployment_instructions(
    environment="kubernetes"
)
```

### 📊 Monitoring & Analytics

```python
# Real-time metrics
metrics = await client.monitoring.get_live_metrics()
print(f"Connections: {metrics.connections_processed:,}")
print(f"Latency: {metrics.avg_latency_ms}ms")

# Security alerts
alerts = await client.monitoring.get_active_alerts()
critical_alerts = [a for a in alerts if a.severity == "critical"]

# Health scoring
health = await client.monitoring.get_health_score()
print(f"Overall Health: {health.overall_score}/100")

if health.risk_factors:
    print("Risk Factors:")
    for risk in health.risk_factors:
        print(f"  • {risk}")
```

### ✅ Compliance Automation

```python
# Validate compliance
compliance = await client.compliance.validate_framework("soc2")
print(f"SOC2 Compliant: {compliance.compliant}")
print(f"Score: {compliance.score}/100")

# Generate compliance report
report = await client.compliance.generate_report(
    framework="pci-dss",
    period_days=30
)

# Automated compliance monitoring
async def monitor_compliance():
    while True:
        for framework in ["soc2", "pci-dss", "hipaa"]:
            result = await client.compliance.validate_framework(framework)
            if not result.compliant:
                await notify_compliance_team(framework, result.issues)
        
        await asyncio.sleep(3600)  # Check hourly
```

### 🔧 Diagnostics & Troubleshooting

```python
# Run comprehensive diagnostics
diagnostics = await client.diagnostics.run_comprehensive_check()
print(f"Tests: {diagnostics.summary.total_tests}")
print(f"Passed: {diagnostics.summary.passed_tests}")
print(f"Failed: {diagnostics.summary.failed_tests}")

# Auto-fix common issues
for result in diagnostics.results:
    if result.status == "failed" and result.fix_suggestions:
        for fix in result.fix_suggestions:
            if fix.auto_fixable:
                await client.diagnostics.apply_auto_fix(result.test_name, fix.title)

# Custom diagnostic tests
custom_test = await client.diagnostics.run_custom_test(
    test_name="custom_connectivity_check",
    target_endpoints=["https://api.example.com"]
)
```

## 🔗 Integration Examples

### Django Integration

```python
# settings.py
VELIKEY_API_KEY = os.getenv("VELIKEY_API_KEY")

# middleware.py
from django.http import JsonResponse
from velikey import AegisClientSync

class VeliKeySecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.client = AegisClientSync(api_key=settings.VELIKEY_API_KEY)
    
    def __call__(self, request):
        # Check security status before processing request
        try:
            status = self.client.get_security_status()
            if status.critical_alerts > 0:
                return JsonResponse({
                    "error": "Security maintenance in progress"
                }, status=503)
        except Exception:
            pass  # Fail open
        
        return self.get_response(request)
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends, HTTPException
from velikey import AegisClient

app = FastAPI()

async def get_velikey_client():
    return AegisClient(api_key=os.getenv("VELIKEY_API_KEY"))

@app.get("/security/status")
async def security_status(client: AegisClient = Depends(get_velikey_client)):
    """Get current security posture."""
    status = await client.get_security_status()
    return {
        "health_score": status.health_score,
        "agents_online": status.agents_online,
        "critical_alerts": status.critical_alerts,
    }

@app.post("/security/policies/{policy_id}/deploy")
async def deploy_policy(
    policy_id: str,
    client: AegisClient = Depends(get_velikey_client)
):
    """Deploy security policy to all agents."""
    result = await client.policies.deploy(policy_id)
    return {"status": "deployed", "details": result}
```

### Celery Task Integration

```python
from celery import Celery
from velikey import AegisClientSync

app = Celery('security_tasks')

@app.task
def check_compliance_status():
    """Periodic compliance check task."""
    client = AegisClientSync(api_key=os.getenv("VELIKEY_API_KEY"))
    
    try:
        # Check all compliance frameworks
        frameworks = ["soc2", "pci-dss", "hipaa"]
        results = {}
        
        for framework in frameworks:
            compliance = client.compliance.validate_framework(framework)
            results[framework] = {
                "compliant": compliance.compliant,
                "score": compliance.score,
                "issues": compliance.issues
            }
        
        # Send results to monitoring system
        send_compliance_metrics(results)
        
    except Exception as e:
        # Log error and alert ops team
        log_error(f"Compliance check failed: {e}")
    finally:
        client.close()

# Schedule the task
app.conf.beat_schedule = {
    'compliance-check': {
        'task': 'check_compliance_status',
        'schedule': 3600.0,  # Every hour
    },
}
```

## 🧪 Testing

```python
# Run tests
pytest

# Run with coverage
pytest --cov=velikey --cov-report=html

# Run specific test categories
pytest -m "not integration"  # Skip integration tests
pytest -k "test_policy"       # Run policy tests only
```

## 📖 Documentation

- **API Reference**: [docs.velikey.com/sdk/python](https://docs.velikey.com/sdk/python)
- **Examples**: [github.com/velikey/velikey-python-sdk/examples](https://github.com/velikey/velikey-python-sdk/tree/main/examples)
- **Tutorials**: [docs.velikey.com/tutorials](https://docs.velikey.com/tutorials)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🛟 Support

- **Documentation**: [docs.velikey.com](https://docs.velikey.com)
- **GitHub Issues**: [github.com/velikey/velikey-python-sdk/issues](https://github.com/velikey/velikey-python-sdk/issues)
- **Community Forum**: [community.velikey.com](https://community.velikey.com)
- **Email**: [sdk-support@velikey.com](mailto:sdk-support@velikey.com)
