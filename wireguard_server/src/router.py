from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.openapi.models import APIKey
from auth import api_key_auth

from manager import manager

router = APIRouter(prefix='/api/v1/interface')


@router.get("/", tags=["interface"])
async def get_interfaces(api_key: APIKey = Depends(api_key_auth)):
    interfaces = manager.interfaces
    return [interface.config.name for interface in interfaces]

@router.post("/", tags=["interface"])
async def create_interface(network_size: int = None ,api_key: APIKey = Depends(api_key_auth)):
    try:
        interface = manager.generate_new_interface(network_prefix=network_size)
        return {"status": "success",
                "interface_name": interface.config.name}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{interface_name}", tags=["interface"])
async def delete_interface(interface_name: str, api_key: APIKey = Depends(api_key_auth)):
    interfaces = manager.interfaces
    for interface in interfaces:
        if interface.config.name == interface_name:
            try:
                interface.delete()
                return {"status": "success"}
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interface not found")


@router.get("/{interface_name}/peers", tags=["interface"])
async def get_interface_peers(interface_name: str, api_key: APIKey = Depends(api_key_auth)):
    interfaces = manager.interfaces
    for interface in interfaces:
        if interface.config.name == interface_name:
            return [peer.name for peer in interface.config.peer_configs]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interface not found")


@router.get("/{interface_name}/peer/{peer_name}/config", tags=["interface"])
async def get_peer_config(interface_name: str, peer_name: str, api_key: APIKey = Depends(api_key_auth)):
    interfaces = manager.interfaces
    for interface in interfaces:
        if interface.config.name == interface_name:
            for peer in interface.config.peer_configs:
                if peer.name == peer_name:
                    return {'config': interface.generate_peer_config(peer)}
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Peer not found")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interface not found")


@router.post("/{interface_name}/peer", tags=["interface"])
async def create_peer(interface_name: str, peer_name: str, api_key: APIKey = Depends(api_key_auth)):
    interfaces = manager.interfaces
    for interface in interfaces:
        if interface.name == interface_name:
            try:
                peer = interface.create_peer(peer_name)
                return {'config': interface.generate_peer_config(peer)}
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interface not found")


@router.patch("/{interface_name}/peer/{peer_name}", tags=["interface"])
async def update_peer(interface_name: str, peer_name: str, name: str, api_key: APIKey = Depends(api_key_auth)):
    interfaces = manager.interfaces
    for interface in interfaces:
        if interface.config.name == interface_name:
            for peer in interface.peer_configs:
                if peer.name == peer_name:
                    try:
                        peer.name = name
                        interface.save_config()
                        return {'config': interface.generate_peer_config(peer)}
                    except Exception as e:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Peer not found")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interface not found")

@router.delete("/{interface_name}/peer/{peer_name}", tags=["interface"])
async def delete_peer(interface_name: str, peer_name: str, api_key: APIKey = Depends(api_key_auth)):
    interfaces = manager.interfaces
    for interface in interfaces:
        if interface.config.name == interface_name:
            for peer in interface.peer_configs:
                if peer.name == peer_name:
                    try:
                        interface.delete_peer(peer)
                        return {"status": "success"}
                    except Exception as e:
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Peer not found")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interface not found")

@router.post("/{interface_name}/", tags=["interface"])
async def change_interface_status(interface_name: str, interface_status: bool, api_key: APIKey = Depends(api_key_auth)):
    interfaces = manager.interfaces
    for interface in interfaces:
        if interface.config.name == interface_name:
            if interface_status:
                interface.run_interface()
                return {"status": "success"}
            else:
                interface.stop_interface()
                return {"status": "success"}


