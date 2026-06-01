"use client";

import { Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { browserApiDelete } from "@/lib/api/client";

export function TenantDeleteButton({ tenantId }: { tenantId: number }) {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);

  async function onDelete() {
    if (!window.confirm("Xóa mềm người thuê này? Dữ liệu hợp đồng và hóa đơn vẫn được giữ lại.")) {
      return;
    }
    setIsDeleting(true);
    try {
      await browserApiDelete(`/tenants/${tenantId}`);
      router.push("/tenants");
      router.refresh();
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <Button disabled={isDeleting} onClick={onDelete} type="button" variant="secondary">
      <Trash2 className="size-4" />
      Xóa mềm
    </Button>
  );
}
