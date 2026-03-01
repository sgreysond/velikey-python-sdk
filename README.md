# VeliKey Aegis Python SDK

[![PyPI version](https://badge.fury.io/py/velikey.svg)](https://badge.fury.io/py/velikey)
[![Python Support](https://img.shields.io/pypi/pyversions/velikey.svg)](https://pypi.org/project/velikey/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Quantum-safe crypto policy management for Python applications**

The VeliKey Python SDK provides a comprehensive interface for managing quantum-safe cryptographic policies, monitoring security posture, and automating compliance workflows.

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install velikey

# Install with optional dependencies
pip install "velikey[dev]"        # Development tools
pip install "velikey[docs]"       # Documentation generation
pip install "velikey[all]"        # All optional dependencies

# Install from source
git clone https://github.com/sgreysond/velikey-python-sdk.git
cd velikey-python-sdk
pip install -e .
```

### Basic Usage

```python
import asyncio
from velikey import AegisClient

async def main():
    # Initialize client with API key
    client = AegisClient(api_key="sk_prod_your-api-key-here")
    
    try:
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
        print(f"📊 Agents Online: {status.agents_online}")
        print(f"🚨 Critical Alerts: {status.critical_alerts}")
        
        # List and manage agents
        agents = await client.agents.list()
        print(f"🤖 Found {len(agents)} agents")
        
        # Show agent details
        for agent in agents[:3]:  # Show first 3 agents
            print(f"  • {agent.name}: {agent.status} (v{agent.version})")
        
        # Check compliance status
        compliance = await client.compliance.validate_framework("soc2")
        print(f"✅ SOC2 Compliance: {'PASS' if compliance.compliant else 'FAIL'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Quick Configuration Examples

**Environment Variables:**
```python
import os
from velikey import AegisClient

# Using environment variables
client = AegisClient(
    api_key=os.getenv("VELIKEY_API_KEY"),
    base_url=os.getenv("VELIKEY_BASE_URL", "https://api.velikey.com")
)
```

**Configuration File:**
```python
import yaml
from velikey import AegisClient

# Load from configuration file
with open("velikey-config.yaml") as f:
    config = yaml.safe_load(f)

client = AegisClient(**config["velikey"])
```

```yaml
# velikey-config.yaml
velikey:
  api_key: "sk_prod_your-api-key"
  base_url: "https://aegis.yourcompany.com:8443"
  timeout: 30
  retry_count: 3
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
    name="SOC2 Production Policy",
    enforcement_mode="enforce",
    post_quantum=True
)
print(f"Created policy: {policy.name} (ID: {policy.id})")

# Custom policy builder with advanced configuration
from velikey import PolicyBuilder

builder = PolicyBuilder()
policy_config = builder \
    .compliance_standard("Custom Security Policy") \
    .post_quantum_ready() \
    .enforcement_mode("enforce") \
    .tls_config({
        "min_version": "1.2",
        "preferred_ciphers": [
            "TLS_AES_256_GCM_SHA384",
            "TLS_KYBER768_P256_SHA256"
        ],
        "required_extensions": ["server_name", "supported_groups"]
    }) \
    .compliance_rules({
        "audit_logging": True,
        "data_retention_days": 90,
        "encryption_at_rest": True
    }) \
    .build()

policy = await client.policies.create("My Custom Policy", policy_config["rules"])

# Deploy to specific agents with staged rollout
deployment = await client.policies.deploy(
    policy.id, 
    target_agents=["agent-1", "agent-2"],
    rollout_strategy="staged",
    rollout_percentage=25  # Start with 25% of agents
)

# Monitor deployment progress
while deployment.status == "in_progress":
    await asyncio.sleep(5)
    deployment = await client.policies.get_deployment(deployment.id)
    print(f"Deployment progress: {deployment.progress}%")

# Promote to full rollout if successful
if deployment.status == "staged_success":
    await client.policies.promote_deployment(deployment.id)
    
# Rollback if needed
if deployment.status == "failed":
    await client.policies.rollback(policy.id)
    print("Deployment rolled back due to failures")

# Policy versioning and history
versions = await client.policies.list_versions(policy.id)
for version in versions:
    print(f"Version {version.version}: {version.created_at} - {version.status}")
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
import logging
import json
from datetime import datetime

app = Celery('security_tasks')
logger = logging.getLogger(__name__)

@app.task(bind=True, max_retries=3)
def check_compliance_status(self):
    """Periodic compliance check task with retry logic."""
    client = AegisClientSync(api_key=os.getenv("VELIKEY_API_KEY"))
    
    try:
        # Check all compliance frameworks
        frameworks = ["soc2", "pci-dss", "hipaa", "gdpr"]
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "frameworks": {}
        }
        
        for framework in frameworks:
            try:
                compliance = client.compliance.validate_framework(framework)
                results["frameworks"][framework] = {
                    "compliant": compliance.compliant,
                    "score": compliance.score,
                    "issues": compliance.issues,
                    "evidence_count": len(compliance.evidence),
                    "last_updated": compliance.last_updated
                }
                
                # Alert on compliance failures
                if not compliance.compliant:
                    send_compliance_alert(framework, compliance.issues)
                    
            except Exception as framework_error:
                logger.error(f"Failed to check {framework}: {framework_error}")
                results["frameworks"][framework] = {
                    "error": str(framework_error),
                    "compliant": False
                }
        
        # Send results to monitoring system
        send_compliance_metrics(results)
        
        # Store results in database
        store_compliance_results(results)
        
        # Generate alerts for degraded compliance
        overall_compliance = calculate_overall_compliance(results)
        if overall_compliance < 0.85:  # 85% threshold
            send_alert(
                level="warning",
                message=f"Overall compliance below threshold: {overall_compliance:.1%}"
            )
        
        return results
        
    except Exception as e:
        logger.error(f"Compliance check failed: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    finally:
        client.close()

@app.task(bind=True)
def automated_policy_deployment(self, policy_id, target_filter="env=production"):
    """Automated policy deployment with safety checks."""
    client = AegisClientSync(api_key=os.getenv("VELIKEY_API_KEY"))
    
    try:
        # Pre-deployment health check
        health = client.get_security_status()
        if health.health_score < 80:
            raise Exception(f"System health too low for deployment: {health.health_score}")
        
        # Get agents matching target filter
        agents = client.agents.list(filter=target_filter)
        if len(agents) == 0:
            raise Exception(f"No agents found matching filter: {target_filter}")
        
        logger.info(f"Deploying policy {policy_id} to {len(agents)} agents")
        
        # Stage deployment (start with 10% of agents)
        staging_count = max(1, len(agents) // 10)
        staging_agents = agents[:staging_count]
        
        deployment = client.policies.deploy(
            policy_id,
            target_agents=[agent.id for agent in staging_agents],
            rollout_strategy="staged"
        )
        
        # Monitor staging deployment
        timeout = 300  # 5 minutes
        start_time = time.time()
        
        while deployment.status == "in_progress":
            if time.time() - start_time > timeout:
                client.policies.rollback(policy_id)
                raise Exception("Staging deployment timed out")
                
            time.sleep(10)
            deployment = client.policies.get_deployment(deployment.id)
        
        if deployment.status != "staged_success":
            raise Exception(f"Staging deployment failed: {deployment.error}")
        
        # Verify staging deployment health
        time.sleep(30)  # Allow metrics to stabilize
        post_deployment_health = client.get_security_status()
        
        if post_deployment_health.health_score < health.health_score - 5:
            client.policies.rollback(policy_id)
            raise Exception("Health score degraded after staging deployment")
        
        # Promote to full deployment
        logger.info("Staging successful, promoting to full deployment")
        full_deployment = client.policies.promote_deployment(deployment.id)
        
        # Monitor full deployment
        while full_deployment.status == "in_progress":
            if time.time() - start_time > timeout * 3:  # Longer timeout for full deployment
                client.policies.rollback(policy_id)
                raise Exception("Full deployment timed out")
                
            time.sleep(15)
            full_deployment = client.policies.get_deployment(full_deployment.id)
        
        if full_deployment.status == "success":
            logger.info(f"Policy {policy_id} successfully deployed to all agents")
            send_deployment_success_notification(policy_id, len(agents))
        else:
            raise Exception(f"Full deployment failed: {full_deployment.error}")
            
        return {
            "policy_id": policy_id,
            "agents_deployed": len(agents),
            "deployment_time": time.time() - start_time,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Policy deployment failed: {e}")
        send_deployment_failure_notification(policy_id, str(e))
        raise
    finally:
        client.close()

# Enhanced schedule configuration
app.conf.beat_schedule = {
    'compliance-check': {
        'task': 'check_compliance_status',
        'schedule': 3600.0,  # Every hour
    },
    'nightly-health-report': {
        'task': 'generate_health_report',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    'weekly-compliance-report': {
        'task': 'generate_weekly_compliance_report',
        'schedule': crontab(day_of_week=1, hour=6, minute=0),  # Monday 6 AM
    },
}

# Additional helper tasks
@app.task
def generate_health_report():
    """Generate comprehensive nightly health report."""
    client = AegisClientSync(api_key=os.getenv("VELIKEY_API_KEY"))
    
    try:
        report = {
            "date": datetime.utcnow().date().isoformat(),
            "security_status": client.get_security_status(),
            "agent_summary": {
                "total": 0,
                "online": 0,
                "offline": 0,
                "outdated": 0
            },
            "policy_summary": {},
            "compliance_status": {},
            "alerts": []
        }
        
        # Collect agent statistics
        agents = client.agents.list()
        report["agent_summary"]["total"] = len(agents)
        
        for agent in agents:
            if agent.status == "online":
                report["agent_summary"]["online"] += 1
            elif agent.status == "offline":
                report["agent_summary"]["offline"] += 1
            
            # Check for outdated agents
            if agent.version != get_latest_agent_version():
                report["agent_summary"]["outdated"] += 1
        
        # Policy deployment status
        policies = client.policies.list()
        for policy in policies:
            report["policy_summary"][policy.name] = {
                "status": policy.status,
                "agents_deployed": len(policy.deployed_agents),
                "compliance_framework": policy.compliance_framework
            }
        
        # Generate and send report
        send_health_report(report)
        store_health_report(report)
        
        return report
        
    finally:
        client.close()

def send_compliance_alert(framework, issues):
    """Send compliance failure alert."""
    message = f"🚨 {framework.upper()} compliance check failed:\n"
    for issue in issues[:5]:  # Limit to top 5 issues
        message += f"• {issue.description}\n"
    
    # Send to Slack, email, etc.
    send_alert(level="critical", message=message)

def calculate_overall_compliance(results):
    """Calculate overall compliance score."""
    scores = []
    for framework_data in results["frameworks"].values():
        if "score" in framework_data:
            scores.append(framework_data["score"])
    
    return sum(scores) / len(scores) if scores else 0.0
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

- **API Reference**: [docs.velikey.com/sdk/python](https://velikey.com/docs/aegis-sdk-python)
- **Examples**: [github.com/velikey/velikey-python-sdk/examples](https://github.com/sgreysond/velikey-python-sdk/tree/main/examples)
- **Tutorials**: [docs.velikey.com/tutorials](https://docs.velikey.com/tutorials)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🛟 Support

- **Documentation**: [docs.velikey.com](https://docs.velikey.com)
- **GitHub Issues**: [github.com/velikey/velikey-python-sdk/issues](https://github.com/sgreysond/velikey-python-sdk/issues)
- **Community Forum**: [community.velikey.com](https://community.velikey.com)
- **Email**: [sdk-support@velikey.com](mailto:sdk-support@velikey.com)
