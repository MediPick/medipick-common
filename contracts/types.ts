/**
 * Canonical TypeScript Interfaces for MediPick Domain Entities
 * Shared across Customer UI, Pharmacy UI, and Admin UI
 */

export type UserRole =
  | 'CUSTOMER'
  | 'PHARMACY_STAFF'
  | 'PHARMACIST'
  | 'PHARMACY_ADMIN'
  | 'COMPLIANCE_OFFICER'
  | 'SUPER_ADMIN';

export interface User {
  id: string;
  phone: string;
  email?: string;
  role: UserRole;
  isActive: boolean;
  createdAt: string;
}

export interface Pharmacy {
  id: string;
  name: string;
  registrationNumber: string;
  slmcNumber?: string;
  phone: string;
  email: string;
  address: string;
  city: string;
  latitude: number;
  longitude: number;
  isOpen: boolean;
  deliveryRadiusKm: number;
  status: 'PENDING' | 'VERIFIED' | 'SUSPENDED';
}

export type OrderStatus =
  | 'PENDING'
  | 'QUOTED'
  | 'CONFIRMED'
  | 'PREPARING'
  | 'DISPENSED'
  | 'COMPLETED'
  | 'CANCELLED'
  | 'REJECTED';

export interface Order {
  id: string;
  orderNumber: string;
  customerId: string;
  pharmacyId: string;
  status: OrderStatus;
  totalAmount: number;
  deliveryFee: number;
  isPickup: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Prescription {
  id: string;
  customerId: string;
  fileKey: string;
  fileUrl: string;
  aiClarityScore: number;
  aiSealDetected: boolean;
  pharmacistNotes?: string;
  status: 'PENDING' | 'VERIFIED' | 'REJECTED';
  createdAt: string;
}

export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data: T;
  meta?: {
    page: number;
    pageSize: number;
    totalItems: number;
    totalPages: number;
  };
}
