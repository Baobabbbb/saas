import { supabase } from '../supabaseClient';

/**
 * Retourne les en-têtes avec le jeton d'accès Supabase si la session existe.
 * Conserve les en-têtes existants (objet simple ou instance Headers).
 */
export async function buildAuthHeaders(existingHeaders = {}) {
  let headers = {};

  if (existingHeaders instanceof Headers) {
    headers = Object.fromEntries(existingHeaders.entries());
  } else {
    headers = { ...existingHeaders };
  }

  const {
    data: { session }
  } = await supabase.auth.getSession();

  if (session?.access_token) {
    headers.Authorization = headers.Authorization || `Bearer ${session.access_token}`;
  }

  return headers;
}

/**
 * Wrapper fetch qui ajoute automatiquement le header Authorization.
 * Authentification requise pour toutes les requêtes.
 */
export async function authFetch(url, options = {}) {
  const { headers, ...rest } = options;
  let finalHeaders = headers || {};

  // Toujours ajouter l'authentification
  finalHeaders = await buildAuthHeaders(finalHeaders);

  return fetch(url, {
    ...rest,
    headers: finalHeaders
  });
}

