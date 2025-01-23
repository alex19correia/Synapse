create extension if not exists "vector" with schema "extensions";


create type "public"."message_status" as enum ('sent', 'delivered', 'error');

create type "public"."session_status" as enum ('active', 'archived', 'deleted');

create table "public"."chat_sessions" (
    "id" uuid not null default uuid_generate_v4(),
    "user_id" text not null,
    "title" text not null default 'Nova Conversa'::text,
    "status" session_status default 'active'::session_status,
    "last_message_at" timestamp with time zone,
    "metadata" jsonb default '{}'::jsonb,
    "created_at" timestamp with time zone default timezone('utc'::text, now()),
    "updated_at" timestamp with time zone default timezone('utc'::text, now())
);


alter table "public"."chat_sessions" enable row level security;

create table "public"."document_embeddings" (
    "id" uuid not null default uuid_generate_v4(),
    "content" text not null,
    "metadata" jsonb default '{}'::jsonb,
    "created_at" timestamp with time zone default timezone('utc'::text, now()),
    "user_id" uuid not null default auth.uid(),
    "embedding" vector,
    "document_id" uuid
);


alter table "public"."document_embeddings" enable row level security;

create table "public"."documents" (
    "id" uuid not null default gen_random_uuid(),
    "title" text not null,
    "content" text,
    "metadata" jsonb default '{}'::jsonb,
    "created_at" timestamp with time zone default CURRENT_TIMESTAMP,
    "updated_at" timestamp with time zone default CURRENT_TIMESTAMP,
    "user_id" uuid not null default auth.uid()
);


alter table "public"."documents" enable row level security;

create table "public"."messages" (
    "id" uuid not null default uuid_generate_v4(),
    "session_id" uuid not null,
    "role" text not null,
    "content" text not null,
    "status" message_status default 'sent'::message_status,
    "metadata" jsonb default '{}'::jsonb,
    "created_at" timestamp with time zone default timezone('utc'::text, now())
);


alter table "public"."messages" enable row level security;

create table "public"."users" (
    "id" uuid not null default gen_random_uuid(),
    "email" text not null,
    "name" text not null,
    "created_At" timestamp with time zone not null default now(),
    "last_login" timestamp with time zone,
    "preferences" jsonb not null default '{}'::jsonb
);


alter table "public"."users" enable row level security;

CREATE UNIQUE INDEX chat_sessions_pkey ON public.chat_sessions USING btree (id);

CREATE UNIQUE INDEX document_embeddings_pkey ON public.document_embeddings USING btree (id);

CREATE UNIQUE INDEX documents_pkey ON public.documents USING btree (id);

CREATE INDEX idx_chat_sessions_last_message ON public.chat_sessions USING btree (last_message_at DESC);

CREATE INDEX idx_chat_sessions_status ON public.chat_sessions USING btree (status);

CREATE INDEX idx_chat_sessions_user_id ON public.chat_sessions USING btree (user_id);

CREATE INDEX idx_messages_created_at ON public.messages USING btree (created_at);

CREATE INDEX idx_messages_session_id ON public.messages USING btree (session_id);

CREATE UNIQUE INDEX messages_pkey ON public.messages USING btree (id);

CREATE UNIQUE INDEX users_email_key ON public.users USING btree (email);

CREATE UNIQUE INDEX users_pkey ON public.users USING btree (id);

alter table "public"."chat_sessions" add constraint "chat_sessions_pkey" PRIMARY KEY using index "chat_sessions_pkey";

alter table "public"."document_embeddings" add constraint "document_embeddings_pkey" PRIMARY KEY using index "document_embeddings_pkey";

alter table "public"."documents" add constraint "documents_pkey" PRIMARY KEY using index "documents_pkey";

alter table "public"."messages" add constraint "messages_pkey" PRIMARY KEY using index "messages_pkey";

alter table "public"."users" add constraint "users_pkey" PRIMARY KEY using index "users_pkey";

alter table "public"."document_embeddings" add constraint "document_embeddings_document_id_fkey" FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE not valid;

alter table "public"."document_embeddings" validate constraint "document_embeddings_document_id_fkey";

alter table "public"."messages" add constraint "messages_role_check" CHECK ((role = ANY (ARRAY['user'::text, 'assistant'::text, 'system'::text]))) not valid;

alter table "public"."messages" validate constraint "messages_role_check";

alter table "public"."messages" add constraint "messages_session_id_fkey" FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE not valid;

alter table "public"."messages" validate constraint "messages_session_id_fkey";

alter table "public"."users" add constraint "users_email_key" UNIQUE using index "users_email_key";

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.match_documents(query_embedding vector, similarity_threshold double precision, match_count integer)
 RETURNS TABLE(id uuid, content text, metadata jsonb, similarity double precision)
 LANGUAGE plpgsql
 SET search_path TO 'public'
AS $function$
BEGIN
    RETURN QUERY
    SELECT
        document_embeddings.id,
        document_embeddings.content,
        document_embeddings.metadata,
        1 - (document_embeddings.embedding <=> query_embedding) AS similarity
    FROM document_embeddings
    WHERE 1 - (document_embeddings.embedding <=> query_embedding) > similarity_threshold
    AND document_embeddings.user_id = auth.uid()
    ORDER BY document_embeddings.embedding <=> query_embedding
    LIMIT match_count;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_documents_updated_at()
 RETURNS trigger
 LANGUAGE plpgsql
 SET search_path TO 'public'
AS $function$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_last_message_timestamp()
 RETURNS trigger
 LANGUAGE plpgsql
 SET search_path TO 'public'
AS $function$
BEGIN
    -- Definir search_path fixo
    SET search_path TO public;
    
    -- Atualizar last_message_at na sessão
    UPDATE public.chat_sessions
    SET last_message_at = NEW.created_at
    WHERE id = NEW.session_id;
    
    RETURN NEW;
END;
$function$
;

CREATE OR REPLACE FUNCTION public.update_updated_at_column()
 RETURNS trigger
 LANGUAGE plpgsql
 SET search_path TO 'public'
AS $function$
BEGIN
    -- Definir search_path fixo
    SET search_path TO public;
    
    -- Atualizar updated_at
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$
;

grant delete on table "public"."chat_sessions" to "anon";

grant insert on table "public"."chat_sessions" to "anon";

grant references on table "public"."chat_sessions" to "anon";

grant select on table "public"."chat_sessions" to "anon";

grant trigger on table "public"."chat_sessions" to "anon";

grant truncate on table "public"."chat_sessions" to "anon";

grant update on table "public"."chat_sessions" to "anon";

grant delete on table "public"."chat_sessions" to "authenticated";

grant insert on table "public"."chat_sessions" to "authenticated";

grant references on table "public"."chat_sessions" to "authenticated";

grant select on table "public"."chat_sessions" to "authenticated";

grant trigger on table "public"."chat_sessions" to "authenticated";

grant truncate on table "public"."chat_sessions" to "authenticated";

grant update on table "public"."chat_sessions" to "authenticated";

grant delete on table "public"."chat_sessions" to "service_role";

grant insert on table "public"."chat_sessions" to "service_role";

grant references on table "public"."chat_sessions" to "service_role";

grant select on table "public"."chat_sessions" to "service_role";

grant trigger on table "public"."chat_sessions" to "service_role";

grant truncate on table "public"."chat_sessions" to "service_role";

grant update on table "public"."chat_sessions" to "service_role";

grant delete on table "public"."document_embeddings" to "anon";

grant insert on table "public"."document_embeddings" to "anon";

grant references on table "public"."document_embeddings" to "anon";

grant select on table "public"."document_embeddings" to "anon";

grant trigger on table "public"."document_embeddings" to "anon";

grant truncate on table "public"."document_embeddings" to "anon";

grant update on table "public"."document_embeddings" to "anon";

grant delete on table "public"."document_embeddings" to "authenticated";

grant insert on table "public"."document_embeddings" to "authenticated";

grant references on table "public"."document_embeddings" to "authenticated";

grant select on table "public"."document_embeddings" to "authenticated";

grant trigger on table "public"."document_embeddings" to "authenticated";

grant truncate on table "public"."document_embeddings" to "authenticated";

grant update on table "public"."document_embeddings" to "authenticated";

grant delete on table "public"."document_embeddings" to "service_role";

grant insert on table "public"."document_embeddings" to "service_role";

grant references on table "public"."document_embeddings" to "service_role";

grant select on table "public"."document_embeddings" to "service_role";

grant trigger on table "public"."document_embeddings" to "service_role";

grant truncate on table "public"."document_embeddings" to "service_role";

grant update on table "public"."document_embeddings" to "service_role";

grant delete on table "public"."documents" to "anon";

grant insert on table "public"."documents" to "anon";

grant references on table "public"."documents" to "anon";

grant select on table "public"."documents" to "anon";

grant trigger on table "public"."documents" to "anon";

grant truncate on table "public"."documents" to "anon";

grant update on table "public"."documents" to "anon";

grant delete on table "public"."documents" to "authenticated";

grant insert on table "public"."documents" to "authenticated";

grant references on table "public"."documents" to "authenticated";

grant select on table "public"."documents" to "authenticated";

grant trigger on table "public"."documents" to "authenticated";

grant truncate on table "public"."documents" to "authenticated";

grant update on table "public"."documents" to "authenticated";

grant delete on table "public"."documents" to "service_role";

grant insert on table "public"."documents" to "service_role";

grant references on table "public"."documents" to "service_role";

grant select on table "public"."documents" to "service_role";

grant trigger on table "public"."documents" to "service_role";

grant truncate on table "public"."documents" to "service_role";

grant update on table "public"."documents" to "service_role";

grant delete on table "public"."messages" to "anon";

grant insert on table "public"."messages" to "anon";

grant references on table "public"."messages" to "anon";

grant select on table "public"."messages" to "anon";

grant trigger on table "public"."messages" to "anon";

grant truncate on table "public"."messages" to "anon";

grant update on table "public"."messages" to "anon";

grant delete on table "public"."messages" to "authenticated";

grant insert on table "public"."messages" to "authenticated";

grant references on table "public"."messages" to "authenticated";

grant select on table "public"."messages" to "authenticated";

grant trigger on table "public"."messages" to "authenticated";

grant truncate on table "public"."messages" to "authenticated";

grant update on table "public"."messages" to "authenticated";

grant delete on table "public"."messages" to "service_role";

grant insert on table "public"."messages" to "service_role";

grant references on table "public"."messages" to "service_role";

grant select on table "public"."messages" to "service_role";

grant trigger on table "public"."messages" to "service_role";

grant truncate on table "public"."messages" to "service_role";

grant update on table "public"."messages" to "service_role";

grant delete on table "public"."users" to "anon";

grant insert on table "public"."users" to "anon";

grant references on table "public"."users" to "anon";

grant select on table "public"."users" to "anon";

grant trigger on table "public"."users" to "anon";

grant truncate on table "public"."users" to "anon";

grant update on table "public"."users" to "anon";

grant delete on table "public"."users" to "authenticated";

grant insert on table "public"."users" to "authenticated";

grant references on table "public"."users" to "authenticated";

grant select on table "public"."users" to "authenticated";

grant trigger on table "public"."users" to "authenticated";

grant truncate on table "public"."users" to "authenticated";

grant update on table "public"."users" to "authenticated";

grant delete on table "public"."users" to "service_role";

grant insert on table "public"."users" to "service_role";

grant references on table "public"."users" to "service_role";

grant select on table "public"."users" to "service_role";

grant trigger on table "public"."users" to "service_role";

grant truncate on table "public"."users" to "service_role";

grant update on table "public"."users" to "service_role";

create policy "Usuários podem atualizar suas próprias sessões"
on "public"."chat_sessions"
as permissive
for update
to public
using (((auth.uid())::text = user_id));


create policy "Usuários podem criar suas próprias sessões"
on "public"."chat_sessions"
as permissive
for insert
to public
with check (((auth.uid())::text = user_id));


create policy "Usuários podem deletar suas próprias sessões"
on "public"."chat_sessions"
as permissive
for delete
to public
using (((auth.uid())::text = user_id));


create policy "Usuários podem ver suas próprias sessões"
on "public"."chat_sessions"
as permissive
for select
to public
using (((auth.uid())::text = user_id));


create policy "Usuários podem atualizar seus próprios document_embeddings"
on "public"."document_embeddings"
as permissive
for update
to public
using ((user_id = auth.uid()))
with check ((user_id = auth.uid()));


create policy "Usuários podem criar seus próprios document_embeddings"
on "public"."document_embeddings"
as permissive
for insert
to public
with check ((user_id = auth.uid()));


create policy "Usuários podem deletar seus próprios document_embeddings"
on "public"."document_embeddings"
as permissive
for delete
to public
using ((user_id = auth.uid()));


create policy "Usuários podem ver seus próprios document_embeddings"
on "public"."document_embeddings"
as permissive
for select
to public
using ((user_id = auth.uid()));


create policy "Usuários podem atualizar seus próprios documents"
on "public"."documents"
as permissive
for update
to public
using ((user_id = auth.uid()))
with check ((user_id = auth.uid()));


create policy "Usuários podem criar seus próprios documents"
on "public"."documents"
as permissive
for insert
to public
with check ((user_id = auth.uid()));


create policy "Usuários podem deletar seus próprios documents"
on "public"."documents"
as permissive
for delete
to public
using ((user_id = auth.uid()));


create policy "Usuários podem ver seus próprios documents"
on "public"."documents"
as permissive
for select
to public
using ((user_id = auth.uid()));


create policy "Usuários podem atualizar mensagens de suas sessões"
on "public"."messages"
as permissive
for update
to public
using ((EXISTS ( SELECT 1
   FROM chat_sessions
  WHERE ((chat_sessions.id = messages.session_id) AND (chat_sessions.user_id = (auth.uid())::text)))));


create policy "Usuários podem criar mensagens em suas sessões"
on "public"."messages"
as permissive
for insert
to public
with check ((EXISTS ( SELECT 1
   FROM chat_sessions
  WHERE ((chat_sessions.id = messages.session_id) AND (chat_sessions.user_id = (auth.uid())::text)))));


create policy "Usuários podem deletar mensagens de suas sessões"
on "public"."messages"
as permissive
for delete
to public
using ((EXISTS ( SELECT 1
   FROM chat_sessions
  WHERE ((chat_sessions.id = messages.session_id) AND (chat_sessions.user_id = (auth.uid())::text)))));


create policy "Usuários podem ver mensagens de suas sessões"
on "public"."messages"
as permissive
for select
to public
using ((EXISTS ( SELECT 1
   FROM chat_sessions
  WHERE ((chat_sessions.id = messages.session_id) AND (chat_sessions.user_id = (auth.uid())::text)))));


create policy "Enable insert for authenticated users only"
on "public"."users"
as permissive
for insert
to public
with check (true);


create policy "Enable read access for all users"
on "public"."users"
as permissive
for select
to public
using (true);


CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON public.chat_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON public.documents FOR EACH ROW EXECUTE FUNCTION update_documents_updated_at();

CREATE TRIGGER update_chat_sessions_last_message AFTER INSERT ON public.messages FOR EACH ROW EXECUTE FUNCTION update_last_message_timestamp();

CREATE TRIGGER update_last_message_timestamp AFTER INSERT ON public.messages FOR EACH ROW EXECUTE FUNCTION update_last_message_timestamp();


