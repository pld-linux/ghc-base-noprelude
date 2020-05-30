%define		pkgname	base-noprelude
Summary:	"base" package sans "Prelude" module
Name:		ghc-%{pkgname}
Version:	4.13.0.0
Release:	1
License:	BSD
Group:		Development/Languages
#Source0Download: http://hackage.haskell.org/package/base-noprelude
Source0:	http://hackage.haskell.org/package/%{pkgname}-%{version}/%{pkgname}-%{version}.tar.gz
# Source0-md5:	954eb0034aa3d09b7bca3de732ba8078
Patch0:		ghc-8.10.patch
URL:		http://hackage.haskell.org/package/base-noprelude
BuildRequires:	ghc >= 6.12.3
BuildRequires:	rpmbuild(macros) >= 1.608
%requires_eq	ghc
Requires(post,postun):	/usr/bin/ghc-pkg
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# debuginfo is not useful for ghc
%define		_enable_debug_packages	0

# don't compress haddock files
%define		_noautocompressdoc	*.haddock

%description
This package simplifies defining custom Preludes without having to use
-XNoImplicitPrelude by re-exporting the full module-hierarchy of the
base-4.13.0.0 package except for the Prelude module.

An usage example for such a Prelude-replacement is available with the
Prelude package.

%prep
%setup -q -n %{pkgname}-%{version}
%patch0 -p1

cat >Setup.lhs<<'EOF'
#!/usr/bin/env runhaskell
> import Distribution.Simple
> main = defaultMain
EOF

%build
runhaskell Setup.lhs configure -v2 \
	--prefix=%{_prefix} \
	--libdir=%{_libdir} \
	--libexecdir=%{_libexecdir} \
	--docdir=%{_docdir}/%{name}-%{version}

runhaskell Setup.lhs build
runhaskell Setup.lhs haddock --executables

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/package.conf.d

runhaskell Setup.lhs copy --destdir=$RPM_BUILD_ROOT

# work around automatic haddock docs installation
%{__rm} -rf %{name}-%{version}-doc
cp -a $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version} %{name}-%{version}-doc
%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

runhaskell Setup.lhs register \
	--gen-pkg-config=$RPM_BUILD_ROOT%{_libdir}/%{ghcdir}/package.conf.d/%{pkgname}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
%ghc_pkg_recache

%postun
%ghc_pkg_recache

%files
%defattr(644,root,root,755)
%{_libdir}/%{ghcdir}/package.conf.d/%{pkgname}.conf
