#!/bin/bash
set -euo pipefail

BDB_SRC=/root/src/db4/db-4.8.30.NC
BDB_PREFIX=/root/src/db4
SRC=/root/src/ruckcoin

echo "==> Berkeley DB"
if [ ! -f "${BDB_PREFIX}/lib/libdb_cxx-4.8.a" ]; then
  cp /usr/share/misc/config.guess /usr/share/misc/config.sub "${BDB_SRC}/dist/"
  chmod +x "${BDB_SRC}/dist/config.guess" "${BDB_SRC}/dist/config.sub"
  mkdir -p "${BDB_SRC}/build_unix"
  cd "${BDB_SRC}/build_unix"
  ../dist/configure --enable-cxx --disable-shared --disable-replication --with-pic --prefix="${BDB_PREFIX}"
  make -j2
  make install
fi
ls -l "${BDB_PREFIX}/lib/libdb_cxx-4.8.a"

echo "==> autogen/configure RuckCoin"
cd "${SRC}"
if [ ! -f configure ]; then
  ./autogen.sh
fi
if [ ! -f Makefile ]; then
  ./configure \
    BDB_LIBS="-L${BDB_PREFIX}/lib -ldb_cxx-4.8" \
    BDB_CFLAGS="-I${BDB_PREFIX}/include" \
    --without-gui \
    --disable-tests \
    --disable-bench \
    --disable-man \
    --with-miniupnpc \
    --enable-zmq \
    --prefix=/root/ruck-prefix
fi

echo "==> compile"
make -j2

echo "==> binaries"
ls -lh src/ravend src/raven-cli
