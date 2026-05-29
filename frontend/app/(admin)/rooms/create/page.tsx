import { ArrowLeft } from "lucide-react";
import Link from "next/link";

import { Card } from "@/components/ui/card";
import { RoomForm, type RoomFloorOption } from "@/features/rooms/room-form";
import { getBuildings, getBuildingTree } from "@/lib/api/server";

export default async function CreateRoomPage() {
  const buildings = await getBuildings();
  const trees = await Promise.all(buildings.items.map((building) => getBuildingTree(building.id)));
  const floorOptions: RoomFloorOption[] = buildings.items.flatMap((building, index) => {
    const tree = trees[index];
    return (
      tree?.floors.map((floor) => ({
        building_id: building.id,
        building_code: building.code,
        building_name: building.name,
        floor_id: floor.id,
        floor_name: floor.name,
        floor_number: floor.floor_number,
      })) ?? []
    );
  });

  return (
    <div className="space-y-6">
      <div>
        <Link className="mb-3 inline-flex items-center gap-2 text-sm text-slate-500" href="/rooms">
          <ArrowLeft className="size-4" />
          Quay lại danh sách
        </Link>
        <h1 className="text-2xl font-semibold text-ink">Thêm phòng</h1>
        <p className="mt-1 text-sm text-slate-500">Tạo phòng bổ sung dưới tầng đã có.</p>
      </div>
      {floorOptions.length > 0 ? (
        <RoomForm floorOptions={floorOptions} mode="create" />
      ) : (
        <Card>
          <p className="text-sm text-slate-500">Cần tạo nhà và tầng trước khi thêm phòng thủ công.</p>
        </Card>
      )}
    </div>
  );
}
