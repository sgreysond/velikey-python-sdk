"""Policy management resource."""

from typing import Dict, List, Optional, Any
from ..models import Policy, PolicyTemplate, ComplianceFramework, PolicyMode
from ..exceptions import ValidationError


class PoliciesResource:
    """Policy management operations."""
    
    def __init__(self, client):
        self._client = client

    async def list(self, active_only: bool = True) -> List[Policy]:
        """List customer policies.
        
        Args:
            active_only: Only return active policies
            
        Returns:
            List of policies
        """
        params = {"active_only": active_only} if active_only else {}
        data = await self._client._request("GET", "/api/policies", params=params)
        return [Policy(**policy) for policy in data["policies"]]

    async def get(self, policy_id: str) -> Policy:
        """Get policy by ID.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            Policy details
        """
        data = await self._client._request("GET", f"/api/policies/{policy_id}")
        return Policy(**data)

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
        payload = {
            "name": name,
            "rules": rules,
            "description": description,
            "enforcement_mode": enforcement_mode,
        }
        data = await self._client._request("POST", "/api/policies", json_data=payload)
        return Policy(**data)

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
        # Get template
        template_data = await self.get_template(template)
        
        # Apply customizations
        rules = template_data.algorithms.copy()
        if post_quantum:
            # Enable PQ algorithms in all components
            for component in ["aegis", "somnus", "logos"]:
                if component in rules and "pq_ready" in rules[component]:
                    if "preferred" not in rules[component]:
                        rules[component]["preferred"] = []
                    rules[component]["preferred"] = (
                        rules[component]["pq_ready"] + rules[component]["preferred"]
                    )
        
        # Apply any additional overrides
        for key, value in overrides.items():
            if "." in key:
                # Handle nested keys like "aegis.preferred"
                parts = key.split(".")
                current = rules
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                rules[key] = value

        return await self.create(
            name=name or template_data.name,
            rules=rules,
            enforcement_mode=enforcement_mode,
        )

    async def update(self, policy_id: str, updates: Dict[str, Any]) -> Policy:
        """Update an existing policy.
        
        Args:
            policy_id: Policy identifier
            updates: Fields to update
            
        Returns:
            Updated policy
        """
        data = await self._client._request("PUT", f"/api/policies/{policy_id}", json_data=updates)
        return Policy(**data)

    async def delete(self, policy_id: str) -> bool:
        """Delete a policy.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            True if successful
        """
        await self._client._request("DELETE", f"/api/policies/{policy_id}")
        return True

    async def deploy(self, policy_id: str, target_agents: Optional[List[str]] = None) -> Dict[str, Any]:
        """Deploy policy to agents.
        
        Args:
            policy_id: Policy to deploy
            target_agents: Specific agents to target (None = all agents)
            
        Returns:
            Deployment status
        """
        payload = {"target_agents": target_agents} if target_agents else {}
        data = await self._client._request("POST", f"/api/policies/{policy_id}/deploy", json_data=payload)
        return data

    async def rollback(self, policy_id: str, version: Optional[int] = None) -> Policy:
        """Rollback policy to previous version.
        
        Args:
            policy_id: Policy identifier
            version: Specific version to rollback to (None = previous)
            
        Returns:
            Rolled back policy
        """
        payload = {"version": version} if version else {}
        data = await self._client._request("POST", f"/api/policies/{policy_id}/rollback", json_data=payload)
        return Policy(**data)

    async def get_versions(self, policy_id: str) -> List[Dict[str, Any]]:
        """Get policy version history.
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            List of policy versions
        """
        data = await self._client._request("GET", f"/api/policies/{policy_id}/versions")
        return data["versions"]

    async def validate(self, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate policy rules.
        
        Args:
            rules: Policy rules to validate
            
        Returns:
            Validation results
        """
        payload = {"rules": rules}
        data = await self._client._request("POST", "/api/policies/validate", json_data=payload)
        return data

    async def get_templates(self) -> List[PolicyTemplate]:
        """Get available policy templates.
        
        Returns:
            List of policy templates
        """
        data = await self._client._request("GET", "/api/policies/templates")
        return [PolicyTemplate(**template) for template in data["templates"]]

    async def get_template(self, template_id: str) -> PolicyTemplate:
        """Get specific policy template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Policy template details
        """
        data = await self._client._request("GET", f"/api/policies/templates/{template_id}")
        return PolicyTemplate(**data)

    async def test_policy(self, policy_id: str, test_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test policy against scenarios.
        
        Args:
            policy_id: Policy to test
            test_scenarios: Test scenarios to run
            
        Returns:
            Test results
        """
        payload = {"scenarios": test_scenarios}
        data = await self._client._request("POST", f"/api/policies/{policy_id}/test", json_data=payload)
        return data

    async def get_compliance_report(self, policy_id: str, framework: ComplianceFramework) -> Dict[str, Any]:
        """Generate compliance report for policy.
        
        Args:
            policy_id: Policy identifier
            framework: Compliance framework to check against
            
        Returns:
            Compliance report
        """
        params = {"framework": framework}
        data = await self._client._request("GET", f"/api/policies/{policy_id}/compliance", params=params)
        return data

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
        return await self.update(policy_id, {"enforcement_mode": mode})

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
