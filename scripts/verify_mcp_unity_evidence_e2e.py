import asyncio, json, os, sys, tempfile
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    with tempfile.TemporaryDirectory() as d:
        root=Path(d); (root/'.frameforge').mkdir(); (root/'Assets').mkdir();(root/'ProjectSettings').mkdir()
        (root/'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 6000.6.4f1')
        (root/'Assets/A.asmdef').write_text(json.dumps({'name':'A','references':['GUID:'+'a'*32]}))
        (root/'.frameforge/profile.json').write_text(json.dumps({'schema_version':1,'selected_plugins':[{'id':'unity','version':'1.0.0'}]}))
        env=dict(os.environ,FRAMEFORGE_MCP_PROJECT_ROOTS=d,PYTHONPATH=os.environ.get('PYTHONPATH', ''))
        server=StdioServerParameters(command=sys.executable,args=['-m','frameforge.mcp_server'],env=env)
        async with stdio_client(server) as (reader,writer):
            async with ClientSession(reader,writer) as client:
                await client.initialize()
                tool_list=await client.list_tools(); assert 'inspect_project' in [t.name for t in tool_list.tools]
                obs={'GUID:'+'a'*32:{'status':'observed_in_package_cache','package':'com.unity.addressables'}}
                result=await client.call_tool('inspect_project',{'project':d,'unity_external_evidence':obs})
                assert not result.is_error, result
                data=result.structured_content or json.loads(result.content[0].text)
                item=data['structural_observations'][0]['unresolved_reference_context'][0]
                assert item['external_evidence']==obs['GUID:'+'a'*32],item
                assert item['resolution']=='unverified' and data['blocking']==False
                failed=await client.call_tool('inspect_project',{'project':'/etc','unity_external_evidence':obs})
                assert failed.is_error,failed
                print('MCP_STDIO_E2E_PASS tools='+str(len(tool_list.tools))+' evidence=1 resolution=unverified root_guard=PASS')
asyncio.run(main())
