"""Policy management resource."""

from typing import Any, Dict, List, Optional

from ..exceptions import NotFoundError, VeliKeyError
from ..models import ComplianceFramework, Policy, PolicyMode, PolicyTemplate


class PoliciesResource:
    """Policy management operations."""
    
    def __init__(self, client):
        self._client = client

    @staticmethod
    def _unsupported(operation: str) -> VeliKeyError:
        return VeliKeyError(
            (
                f"Unsupported operation: {operation}. "
                "Current Axis route contract supports listing policies via GET /api/policies "
                "and rollout execution via /api/rollouts/*."
            ),
            status_code=501,
        )

    async def list(self, active_only: bool = True) -> List[Policy]:
        """List customer policies.
        
        Args:
            active_only: Only return active policies
            
        Returns:
            List of policies
        """
        params = {"isActive": str(active_only).lower()} if active_only else {}
        data = await self._client._request("GET", "/api/policies", params=params)
        policies = data.get("policies", [])
        return [Policy(**policy) for policy in policies]

    async def get(self, policy_id: str) -> Policy:
        """Get policy by ID.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            Policy details
        """
        policies = await self.list(active_only=False)
        for policy in policies:
            if str(policy.id) == str(policy_id):
                return policy
        raise NotFoundError(f"Policy not found: {policy_id}", status_code=404)

    async def create(
        self,
        name: str,
        rules: Dict[str, Any],
        description: Optional[str] = None,
        enforcement_mode: PolicyMode = PolicyMode.OBSERVE,
    ) -> Policy:
        """Create a new policy.
        
        Args:
            name: Policy name
            rules: Policy rules configuration
            description: Optional description
            enforcement_mode: Enforcement mode
            
        Returns:
            Created policy
        """
        raise self._unsupported("policies.create")

    async def create_from_template(
        self,
        template: str,
        name: Optional[str] = None,
        enforcement_mode: PolicyMode = PolicyMode.OBSERVE,
        post_quantum: bool = False,
        **overrides,
    ) -> Policy:
        """Create policy from compliance template.
        
        Args:
            template: Template name (soc2, pci-dss, hipaa, gdpr)
            name: Custom policy name
            enforcement_mode: Enforcement mode
            post_quantum: Enable post-quantum algorithms
            **overrides: Template customizations
            
        Returns:
            Created policy
        """
        raise self._unsupported("policies.create_from_template")

    async def update(self, policy_id: str, updates: Dict[str, Any]) -> Policy:
        """Update an existing policy.
        
        Args:
            policy_id: Policy identifier
            updates: Fields to update
            
        Returns:
            Updated policy
        """
        raise self._unsupported("policies.update")

    async def delete(self, policy_id: str) -> bool:
        """Delete a policy.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            True if successful
        """
        raise self._unsupported("policies.delete")

    async def deploy(self, policy_id: str, target_agents: Optional[List[str]] = None) -> Dict[str, Any]:
        """Deploy policy to agents.
        
        Args:
            policy_id: Policy to deploy
            target_agents: Specific agents to target (None = all agents)
            
        Returns:
            Deployment status
        """
        raise self._unsupported("policies.deploy")

    async def rollback(self, policy_id: str, version: Optional[int] = None) -> Policy:
        """Rollback policy to previous version.
        
        Args:
            policy_id: Policy identifier
            version: Specific version to rollback to (None = previous)
            
        Returns:
            Rolled back policy
        """
        raise self._unsupported("policies.rollback")

    async def get_versions(self, policy_id: str) -> List[Dict[str, Any]]:
        """Get policy version history.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            List of policy versions
        """
        raise self._unsupported("policies.get_versions")

    async def validate(self, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate policy rules.
        
        Args:
            rules: Policy rules to validate
            
        Returns:
            Validation results
        """
        raise self._unsupported("policies.validate")

    async def get_templates(self) -> List[PolicyTemplate]:
        """Get available policy templates.
        
        Returns:
            List of policy templates
        """
        data = await self._client._request("GET", "/api/compliance-bundles/templates")
        templates = data.get("templates", [])
        return [PolicyTemplate(**template) for template in templates]

    async def get_template(self, template_id: str) -> PolicyTemplate:
        """Get specific policy template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Policy template details
        """
        data = await self._client._request(
            "GET",
            "/api/compliance-bundles/templates",
            params={"id": template_id},
        )
        template = data.get("template")
        if not isinstance(template, dict):
            raise NotFoundError(f"Template not found: {template_id}", status_code=404)
        return PolicyTemplate(**template)

    async def test_policy(self, policy_id: str, test_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test policy against scenarios.
        
        Args:
            policy_id: Policy to test
            test_scenarios: Test scenarios to run
            
        Returns:
            Test results
        """
        raise self._unsupported("policies.test_policy")

    async def get_compliance_report(self, policy_id: str, framework: ComplianceFramework) -> Dict[str, Any]:
        """Generate compliance report for policy.
        
        Args:
            policy_id: Policy identifier
            framework: Compliance framework to check against
            
        Returns:
            Compliance report
        """
        raise self._unsupported("policies.get_compliance_report")

    # Convenience methods for common operations
    async def enable_post_quantum(self, policy_id: str) -> Policy:
        """Enable post-quantum cryptography for a policy.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            Updated policy
        """
        policy = await self.get(policy_id)
        
        # Update rules to enable PQ
        updated_rules = policy.rules.copy()
        for component in ["aegis", "somnus", "logos"]:
            if component in updated_rules and "pq_ready" in updated_rules[component]:
                pq_algorithms = updated_rules[component]["pq_ready"]
                if "preferred" not in updated_rules[component]:
                    updated_rules[component]["preferred"] = []
                updated_rules[component]["preferred"] = pq_algorithms + updated_rules[component]["preferred"]
        
        return await self.update(policy_id, {"rules": updated_rules})

    async def set_enforcement_mode(self, policy_id: str, mode: PolicyMode) -> Policy:
        """Change policy enforcement mode.
        
        Args:
            policy_id: Policy identifier
            mode: New enforcement mode
            
        Returns:
            Updated policy
        """
        return await self.update(
            policy_id,
            {"enforcement_mode": mode.value if isinstance(mode, PolicyMode) else mode},
        )

    async def clone_policy(self, policy_id: str, new_name: str) -> Policy:
        """Clone an existing policy.
        
        Args:
            policy_id: Source policy identifier
            new_name: Name for cloned policy
            
        Returns:
            Cloned policy
        """
        source_policy = await self.get(policy_id)
        return await self.create(
            name=new_name,
            rules=source_policy.rules,
            description=f"Cloned from {source_policy.name}",
            enforcement_mode=source_policy.enforcement_mode,
        )
