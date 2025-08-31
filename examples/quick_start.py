#!/usr/bin/env python3
"""
VeliKey Aegis Python SDK - Quick Start Example

This example demonstrates the most common VeliKey operations:
- Setting up quantum-safe crypto policies
- Deploying and monitoring agents
- Checking compliance status
- Handling security alerts
"""

import asyncio
import os
from velikey import AegisClient, PolicyMode, ComplianceFramework


async def main():
    """Main example function."""
    # Initialize client
    api_key = os.getenv("VELIKEY_API_KEY")
    if not api_key:
        print("Please set VELIKEY_API_KEY environment variable")
        return

    async with AegisClient(api_key=api_key) as client:
        print("🛡️ VeliKey Aegis SDK Quick Start")
        print("=" * 50)

        # 1. Quick setup for new customers
        print("\n1. 🚀 Quick Setup")
        setup_result = await client.quick_setup(
            compliance_framework="soc2",
            enforcement_mode="observe",  # Start in observe mode
            post_quantum=True,
        )
        print(f"✅ Created policy: {setup_result.policy_name}")
        print(f"📋 Next steps: {', '.join(setup_result.next_steps)}")

        # 2. List and monitor agents
        print("\n2. 🤖 Agent Management")
        agents = await client.agents.list()
        print(f"📊 Found {len(agents)} agents")
        
        for agent in agents:
            status_emoji = "✅" if agent.status == "online" else "❌"
            print(f"  {status_emoji} {agent.name} ({agent.version}) - {agent.status}")
            print(f"    Location: {agent.location}")
            print(f"    Capabilities: {', '.join(agent.capabilities)}")

        # 3. Policy management
        print("\n3. 📋 Policy Management")
        policies = await client.policies.list()
        print(f"📊 Found {len(policies)} active policies")
        
        for policy in policies:
            mode_emoji = "👁️" if policy.enforcement_mode == "observe" else "🛡️"
            print(f"  {mode_emoji} {policy.name} ({policy.compliance_framework})")
            print(f"    Mode: {policy.enforcement_mode}")
            print(f"    Active: {policy.is_active}")

        # 4. Security status overview
        print("\n4. 🔐 Security Status")
        security_status = await client.get_security_status()
        print(f"📊 Health Score: {security_status.health_score}/100")
        print(f"🤖 Agents Online: {security_status.agents_online}")
        print(f"📋 Active Policies: {security_status.policies_active}")
        print(f"🚨 Critical Alerts: {security_status.critical_alerts}")
        
        if security_status.recommendations:
            print("💡 Recommendations:")
            for rec in security_status.recommendations[:3]:  # Show top 3
                print(f"  • {rec}")

        # 5. Compliance checking
        print("\n5. ✅ Compliance Status")
        if policies:
            policy_id = policies[0].id
            compliance_report = await client.policies.get_compliance_report(
                policy_id, ComplianceFramework.SOC2
            )
            print(f"📊 SOC2 Compliance Score: {compliance_report.get('score', 'N/A')}/100")
            
            violations = compliance_report.get('violations', [])
            if violations:
                print(f"⚠️ Found {len(violations)} compliance issues:")
                for violation in violations[:3]:  # Show top 3
                    print(f"  • {violation}")
            else:
                print("✅ No compliance violations detected")

        # 6. Real-time monitoring
        print("\n6. 📊 Real-time Monitoring")
        metrics = await client.monitoring.get_live_metrics()
        print(f"🔗 Connections Processed: {metrics.connections_processed:,}")
        print(f"📈 Bytes Analyzed: {metrics.bytes_analyzed:,}")
        print(f"⏱️ Average Latency: {metrics.avg_latency_ms}ms")
        print(f"🆙 Uptime: {metrics.uptime_percentage:.1f}%")

        # 7. Security alerts
        print("\n7. 🚨 Security Alerts")
        alerts = await client.monitoring.get_active_alerts()
        if alerts:
            print(f"Found {len(alerts)} active alerts:")
            for alert in alerts[:3]:  # Show top 3
                severity_emoji = {
                    "info": "ℹ️",
                    "warning": "⚠️", 
                    "error": "❌",
                    "critical": "🔥",
                    "emergency": "🚨"
                }.get(alert.severity, "❓")
                print(f"  {severity_emoji} {alert.title}")
                print(f"    {alert.description}")
        else:
            print("✅ No active security alerts")

        # 8. Diagnostics
        print("\n8. 🔧 System Diagnostics")
        diagnostic_suite = await client.diagnostics.run_comprehensive_check()
        print(f"🧪 Ran {diagnostic_suite.summary.total_tests} diagnostic tests")
        print(f"✅ Passed: {diagnostic_suite.summary.passed_tests}")
        print(f"⚠️ Warnings: {diagnostic_suite.summary.warning_tests}")
        print(f"❌ Failed: {diagnostic_suite.summary.failed_tests}")
        
        if diagnostic_suite.summary.critical_issues:
            print("🔥 Critical Issues:")
            for issue in diagnostic_suite.summary.critical_issues:
                print(f"  • {issue}")

        print(f"\n🏥 Overall System Health: {diagnostic_suite.summary.overall_health}")

        print("\n" + "=" * 50)
        print("🎉 Quick start complete! Check the VeliKey dashboard for more details.")
        print("📚 Documentation: https://docs.velikey.com/sdk/python")


if __name__ == "__main__":
    asyncio.run(main())
