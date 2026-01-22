"use client";

import { useEffect, useState } from "react";
import { Users, UserPlus, Loader2, Trash2, Shield, ShieldCheck, Eye } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useBrand } from "../layout";
import { useAuth } from "@/hooks/use-auth";
import { useToast } from "@/hooks/use-toast";
import * as api from "@/lib/api";
import type { BrandMember, BrandRole } from "@/types";

const roleDescriptions: Record<BrandRole, string> = {
  owner: "Full access including team management and deletion",
  editor: "Can upload, analyze, and generate content",
  viewer: "Can view profiles and outputs only",
};

const roleIcons: Record<BrandRole, React.ReactNode> = {
  owner: <ShieldCheck className="h-4 w-4" />,
  editor: <Shield className="h-4 w-4" />,
  viewer: <Eye className="h-4 w-4" />,
};

export default function TeamPage() {
  const { brand, userRole, refetch } = useBrand();
  const { user, token } = useAuth();
  const { toast } = useToast();

  const [members, setMembers] = useState<BrandMember[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [removeMemberId, setRemoveMemberId] = useState<string | null>(null);
  const [isRemoving, setIsRemoving] = useState(false);

  // Add member form
  const [newMemberEmail, setNewMemberEmail] = useState("");
  const [newMemberRole, setNewMemberRole] = useState<BrandRole>("viewer");

  const isOwner = userRole === "owner";

  useEffect(() => {
    if (!token || !brand) return;

    api
      .getBrandMembers(token, brand.id)
      .then(setMembers)
      .catch((err) => {
        toast({
          title: "Error loading team",
          description: err instanceof Error ? err.message : "Unknown error",
          variant: "destructive",
        });
      })
      .finally(() => setIsLoading(false));
  }, [token, brand, toast]);

  const handleAddMember = async () => {
    if (!token || !brand || !newMemberEmail) return;

    setIsAdding(true);
    try {
      const member = await api.addBrandMember(token, brand.id, {
        email: newMemberEmail,
        role: newMemberRole,
      });
      setMembers((prev) => [...prev, member]);
      setShowAddDialog(false);
      setNewMemberEmail("");
      setNewMemberRole("viewer");
      toast({ title: "Member added", description: `${newMemberEmail} has been invited` });
      refetch();
    } catch (err) {
      toast({
        title: "Failed to add member",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setIsAdding(false);
    }
  };

  const handleUpdateRole = async (memberId: string, newRole: BrandRole) => {
    if (!token || !brand) return;

    try {
      await api.updateBrandMember(token, brand.id, memberId, { role: newRole });
      setMembers((prev) =>
        prev.map((m) => (m.id === memberId ? { ...m, role: newRole } : m))
      );
      toast({ title: "Role updated" });
      refetch();
    } catch (err) {
      toast({
        title: "Failed to update role",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      });
    }
  };

  const handleRemoveMember = async () => {
    if (!token || !brand || !removeMemberId) return;

    setIsRemoving(true);
    try {
      await api.removeBrandMember(token, brand.id, removeMemberId);
      setMembers((prev) => prev.filter((m) => m.id !== removeMemberId));
      toast({ title: "Member removed" });
      refetch();
    } catch (err) {
      toast({
        title: "Failed to remove member",
        description: err instanceof Error ? err.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setIsRemoving(false);
      setRemoveMemberId(null);
    }
  };

  const getInitials = (name?: string, email?: string) => {
    if (name) {
      return name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);
    }
    if (email) {
      return email.slice(0, 2).toUpperCase();
    }
    return "??";
  };

  if (!brand) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Team</h1>
          <p className="text-muted-foreground">
            Manage who has access to this brand
          </p>
        </div>
        {isOwner && (
          <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
            <DialogTrigger asChild>
              <Button>
                <UserPlus className="mr-2 h-4 w-4" />
                Add Member
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Team Member</DialogTitle>
                <DialogDescription>
                  Invite someone to collaborate on this brand
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={newMemberEmail}
                    onChange={(e) => setNewMemberEmail(e.target.value)}
                    placeholder="colleague@example.com"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Role</Label>
                  <Select
                    value={newMemberRole}
                    onValueChange={(v) => setNewMemberRole(v as BrandRole)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="viewer">Viewer</SelectItem>
                      <SelectItem value="editor">Editor</SelectItem>
                      <SelectItem value="owner">Owner</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground">
                    {roleDescriptions[newMemberRole]}
                  </p>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowAddDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleAddMember} disabled={!newMemberEmail || isAdding}>
                  {isAdding && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Add Member
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {/* Role Legend */}
      <div className="grid gap-4 md:grid-cols-3">
        {(["owner", "editor", "viewer"] as BrandRole[]).map((role) => (
          <Card key={role}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                {roleIcons[role]}
                {role.charAt(0).toUpperCase() + role.slice(1)}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">{roleDescriptions[role]}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Members Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Team Members
          </CardTitle>
          <CardDescription>
            {members.length} member{members.length !== 1 ? "s" : ""}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Member</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Joined</TableHead>
                  {isOwner && <TableHead className="text-right">Actions</TableHead>}
                </TableRow>
              </TableHeader>
              <TableBody>
                {members.map((member) => {
                  const isCurrentUser = member.user_id === user?.id;
                  const isSoleOwner =
                    member.role === "owner" &&
                    members.filter((m) => m.role === "owner").length === 1;

                  return (
                    <TableRow key={member.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Avatar>
                            <AvatarFallback>
                              {getInitials(member.user?.full_name, member.user?.email)}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-medium">
                              {member.user?.full_name || member.user?.email || "Unknown"}
                              {isCurrentUser && (
                                <Badge variant="outline" className="ml-2">
                                  You
                                </Badge>
                              )}
                            </p>
                            {member.user?.full_name && (
                              <p className="text-sm text-muted-foreground">
                                {member.user.email}
                              </p>
                            )}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        {isOwner && !isCurrentUser && !isSoleOwner ? (
                          <Select
                            value={member.role}
                            onValueChange={(v) => handleUpdateRole(member.id, v as BrandRole)}
                          >
                            <SelectTrigger className="w-32">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="viewer">Viewer</SelectItem>
                              <SelectItem value="editor">Editor</SelectItem>
                              <SelectItem value="owner">Owner</SelectItem>
                            </SelectContent>
                          </Select>
                        ) : (
                          <Badge variant="secondary" className="flex items-center gap-1 w-fit">
                            {roleIcons[member.role]}
                            {member.role}
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {new Date(member.created_at).toLocaleDateString()}
                      </TableCell>
                      {isOwner && (
                        <TableCell className="text-right">
                          {!isCurrentUser && !isSoleOwner && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => setRemoveMemberId(member.id)}
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          )}
                        </TableCell>
                      )}
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Remove Confirmation Dialog */}
      <AlertDialog open={!!removeMemberId} onOpenChange={() => setRemoveMemberId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove Team Member</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to remove this member from the team? They will lose access to this brand.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isRemoving}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleRemoveMember} disabled={isRemoving}>
              {isRemoving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Remove
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
