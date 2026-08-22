const configuredBase =
  import.meta.env.VITE_API_BASE_URL?.trim()


const API_BASE_URL =
  configuredBase || '/api'


export class ProfitLensApiError
  extends Error {
  status: number

  details?: unknown


  constructor(
    message: string,
    status: number,
    details?: unknown
  ) {
    super(message)

    this.name =
      'ProfitLensApiError'

    this.status =
      status

    this.details =
      details
  }
}


type RequestOptions = {
  method?:
    | 'GET'
    | 'POST'
    | 'PATCH'
    | 'DELETE'

  body?: unknown

  signal?: AbortSignal
}


export async function
requestV2<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const response =
    await fetch(
      `${API_BASE_URL}${path}`,
      {
        method:
          options.method
          ?? 'GET',

        headers: {
          'Content-Type':
            'application/json',
        },

        body:
          options.body
            !== undefined
            ? JSON.stringify(
                options.body
              )
            : undefined,

        signal:
          options.signal,
      }
    )


  if (!response.ok) {
    let details:
      unknown = null

    try {
      details =
        await response.json()
    } catch {
      details =
        await response.text()
    }

    const message =
      (
        typeof details
        === 'object'
        && details !== null
        && 'detail' in details
      )
        ? String(
            (
              details as {
                detail?: unknown
              }
            ).detail
          )
        : (
            `ProfitLens API request failed `
            + `with status ${response.status}.`
          )

    throw new ProfitLensApiError(
      message,
      response.status,
      details
    )
  }


  if (
    response.status
    === 204
  ) {
    return undefined as T
  }


  return (
    await response.json()
  ) as T
}
