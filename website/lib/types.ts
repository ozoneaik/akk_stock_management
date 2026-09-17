export type ProductDTO = {
  id: string;
  sku: string | null;
  barcode: string | null;
  name: string;
  commonName: string | null;
  description: string | null;
  imageUrl: string | null;
  categoryId: string;
  categoryName: string;
  baseUnit: string;
  packUnit: string | null;
  unitsPerPack: number;
  currentStock: number;
  minStockAlert: number;
  isActive: boolean;
  prices: Record<string, { price: number; discount: number }>;
};

export type CategoryDTO = {
  id: string;
  name: string;
};

export type UserDTO = {
  id: string;
  username: string;
  name: string;
  role: string;
  roleLabel: string;
  isActive: boolean;
};

export type ActivityLogDTO = {
  id: string;
  action: string;
  entityType: string;
  entityId: string;
  description: string;
  userRole: string;
  createdAt: string;
  actionLabel: string;
  userDisplayName: string;
  username: string | null;
};
