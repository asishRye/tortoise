-- upgrade --
ALTER TABLE "users" RENAME COLUMN "family_name" TO "family_name_changed";
-- downgrade --
ALTER TABLE "users" RENAME COLUMN "family_name_changed" TO "family_name";
