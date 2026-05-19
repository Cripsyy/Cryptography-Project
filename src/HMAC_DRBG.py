import hashlib
import hmac

_OUTLEN = 32
_SEEDLEN = 55
_MAX_BYTES_PER_REQUEST = 65536
_RESEED_INTERVAL = 2**48


class HMAC_DRBG:

    def __init__(
        self,
        entropy_input,
        nonce=b"",
        personalization_string=b"",
        reseed_interval=_RESEED_INTERVAL,
    ):
        if len(entropy_input) < _SEEDLEN:
            raise ValueError(
                f"entropy_input must be at least {_SEEDLEN} bytes, "
                f"got {len(entropy_input)}"
            )

        self._reseed_interval = reseed_interval
        self._reseed_counter = 0

        seed_material = entropy_input + nonce + personalization_string

        self._K = b"\x00" * _OUTLEN
        self._V = b"\x01" * _OUTLEN  # <-- AICI A FOST CORECTAT (_OUTLEN în loc de _SEEDLEN)

        self._update(seed_material)

        self._reseed_counter = 1

    def _update(self, provided_data):
        self._K = hmac.new(
            self._K, self._V + b"\x00" + provided_data, hashlib.sha256
        ).digest()
        self._V = hmac.new(self._K, self._V, hashlib.sha256).digest()

        if provided_data:
            self._K = hmac.new(
                self._K, self._V + b"\x01" + provided_data, hashlib.sha256
            ).digest()
            self._V = hmac.new(self._K, self._V, hashlib.sha256).digest()

    def reseed(self, entropy_input, additional_input=b""):
        if len(entropy_input) < _SEEDLEN:
            raise ValueError(
                f"entropy_input must be at least {_SEEDLEN} bytes, "
                f"got {len(entropy_input)}"
            )

        seed_material = entropy_input + additional_input
        self._update(seed_material)
        self._reseed_counter = 1

    def generate(self, num_bytes, additional_input=b""):
        if self._reseed_counter > self._reseed_interval:
            raise RuntimeError(
                "Reseed required: reseed_counter exceeds reseed_interval"
            )

        if num_bytes > _MAX_BYTES_PER_REQUEST:
            raise ValueError(
                f"Cannot generate more than {_MAX_BYTES_PER_REQUEST} "
                f"bytes per request, got {num_bytes}"
            )

        if additional_input:
            self._update(additional_input)

        temp = b""
        while len(temp) < num_bytes:
            self._V = hmac.new(self._K, self._V, hashlib.sha256).digest()
            temp += self._V

        result = temp[:num_bytes]

        self._update(additional_input)

        self._reseed_counter += 1

        return result