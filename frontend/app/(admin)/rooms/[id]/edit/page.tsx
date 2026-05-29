import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";

import { RoomForm } from "@/features/rooms/room-form";
import { getRoom } from "@/lib/api/server";

export default async function EditRoomPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const room = await getRoom(Number(id));
  if (!room) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <div>
        <Link
          className="mb-3 inline-flex items-center gap-2 text-sm text-slate-500 hover:text-ink"
          href={`/rooms/${room.id}`}
        >
          <ArrowLeft className="size-4" />
          Quay lại phòng
        </Link>
        <h1 className="text-2xl font-semibold text-ink">Sửa phòng {room.code}</h1>
        <p className="mt-1 text-sm text-slate-500">Cập nhật thông tin vận hành của phòng.</p>
      </div>
      <RoomForm mode="edit" room={room} />
    </div>
  );
}
